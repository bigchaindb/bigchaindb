"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation on ReadTheDocs:
 - https://docs.bigchaindb.com/projects/server/en/latest/drivers-clients/
   http-client-server-api.html
"""
import logging

from flask import current_app, request
from flask_restful import Resource, reqparse

from bigchaindb.common.exceptions import (
    AmountError,
    DoubleSpend,
    InvalidHash,
    InvalidSignature,
    SchemaValidationError,
    OperationError,
    TransactionDoesNotExist,
    TransactionOwnerError,
    TransactionNotInValidBlock,
    ValidationError,
)

import bigchaindb
from bigchaindb import Bigchain
from bigchaindb.models import Transaction
from bigchaindb.web.views.base import make_error
from bigchaindb.web.views import parameters

logger = logging.getLogger(__name__)

TRANSACTION_STATUSES = (
    Bigchain.BLOCK_VALID,
    Bigchain.BLOCK_UNDECIDED,
    Bigchain.TX_IN_BACKLOG,
)


class TransactionApi(Resource):
    def get(self, tx_id):
        """API endpoint to get details about a transaction.

        Args:
            tx_id (str): the id of the transaction.

        Return:
            A JSON string containing the data about the transaction.
        """
        parser = reqparse.RequestParser(trim=True)
        parser.add_argument(
            'status',
            default='valid',
            type=str,
            choices=TRANSACTION_STATUSES,
            case_sensitive=False,
            help=('Unsupported transaction status: {error_msg}. ' +
                  'Must be one of: ("{}", "{}", "{}")'.format(
                      *TRANSACTION_STATUSES)),
        )
        args = parser.parse_args(strict=True)
        requested_status = args['status']

        pool = current_app.config['bigchain_pool']

        with pool() as bigchain:
            tx, status = bigchain.get_transaction(tx_id, include_status=True)

        if not tx or status != requested_status:
            return make_error(
                404,
                message=(
                    'Transaction with id: "{}" and '
                    'status: "{}" could not be found.'
                ).format(tx_id, requested_status)
            )

        return tx.to_dict()


class TransactionListApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('operation', type=parameters.valid_operation)
        parser.add_argument('asset_id', type=parameters.valid_txid,
                            required=True)
        args = parser.parse_args()

        with current_app.config['bigchain_pool']() as bigchain:
            txs = bigchain.get_transactions_filtered(**args)

        return [tx.to_dict() for tx in txs]

    def post(self):
        """API endpoint to push transactions to the Federation.

        Return:
            A ``dict`` containing the data about the transaction.
        """
        pool = current_app.config['bigchain_pool']
        monitor = current_app.config['monitor']

        # `force` will try to format the body of the POST request even if the
        # `content-type` header is not set to `application/json`
        tx = request.get_json(force=True)

        try:
            tx_obj = Transaction.from_dict(tx)
        except SchemaValidationError as e:
            return make_error(
                400,
                message='Invalid transaction schema: {}'.format(
                    e.__cause__.message)
            )
        except (ValidationError, InvalidSignature) as e:
            return make_error(
                400,
                'Invalid transaction ({}): {}'.format(type(e).__name__, e)
            )

        with pool() as bigchain:
            try:
                bigchain.validate_transaction(tx_obj)
            except (ValueError,
                    OperationError,
                    TransactionDoesNotExist,
                    TransactionOwnerError,
                    DoubleSpend,
                    InvalidHash,
                    InvalidSignature,
                    TransactionNotInValidBlock,
                    AmountError) as e:
                return make_error(
                    400,
                    'Invalid transaction ({}): {}'.format(type(e).__name__, e)
                )
            else:
                rate = bigchaindb.config['statsd']['rate']
                with monitor.timer('write_transaction', rate=rate):
                    bigchain.write_transaction(tx_obj)

        return tx, 202
