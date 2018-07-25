"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation: http://bigchaindb.com/http-api
"""
import logging

from flask import current_app, request, jsonify
from flask_restful import Resource, reqparse

from bigchaindb.common.exceptions import SchemaValidationError, ValidationError
from bigchaindb.web.views.base import make_error
from bigchaindb.web.views import parameters
from bigchaindb.models import Transaction


logger = logging.getLogger(__name__)


class TransactionApi(Resource):
    def get(self, tx_id):
        """API endpoint to get details about a transaction.

        Args:
            tx_id (str): the id of the transaction.

        Return:
            A JSON string containing the data about the transaction.
        """
        pool = current_app.config['bigchain_pool']

        with pool() as bigchain:
            tx, status = bigchain.get_transaction(tx_id, include_status=True)

        if not tx or status is not bigchain.TX_VALID:
            return make_error(404)

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
        parser = reqparse.RequestParser()
        parser.add_argument('mode', type=parameters.valid_mode,
                            default='broadcast_tx_async')
        args = parser.parse_args()
        mode = str(args['mode'])

        pool = current_app.config['bigchain_pool']

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
        except ValidationError as e:
            return make_error(
                400,
                'Invalid transaction ({}): {}'.format(type(e).__name__, e)
            )

        with pool() as bigchain:
            try:
                bigchain.validate_transaction(tx_obj)
            except ValidationError as e:
                return make_error(
                    400,
                    'Invalid transaction ({}): {}'.format(type(e).__name__, e)
                )
            else:
                status_code, message = bigchain.write_transaction(tx_obj, mode)

        if status_code == 202:
            response = jsonify(tx)
            response.status_code = 202
            return response
        else:
            return make_error(status_code, message)
