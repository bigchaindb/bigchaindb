from copy import deepcopy
from uuid import uuid4
import logging
from collections import namedtuple

import requests

from bigchaindb import backend
from bigchaindb import Bigchain
from bigchaindb.models import Transaction
from bigchaindb.common.exceptions import SchemaValidationError, ValidationError
from bigchaindb.tendermint.utils import encode_transaction


logger = logging.getLogger(__name__)

ENDPOINT = 'http://localhost:46657/'


class BigchainDB(Bigchain):

    def post_transaction(self, transaction):
        """Submit a valid transaction to the mempool."""

        payload = {
            'method': 'broadcast_tx_async',
            'jsonrpc': '2.0',
            'params': [encode_transaction(transaction.to_dict())],
            'id': str(uuid4())
        }
        # TODO: handle connection errors!
        requests.post(ENDPOINT, json=payload)

    def write_transaction(self, transaction):
        # This method offers backward compatibility with the Web API.
        """Submit a valid transaction to the mempool."""

        self.post_transaction(transaction)

    def store_transaction(self, transaction):
        """Store a valid transaction to the transactions collection."""

        transaction = deepcopy(transaction.to_dict())
        if transaction['operation'] == 'CREATE':
            asset = transaction.pop('asset')
            asset['id'] = transaction['id']
            if asset['data']:
                backend.query.store_asset(self.connection, asset)

        return backend.query.store_transaction(self.connection, transaction)

    def get_transaction(self, transaction_id, include_status=False):
        transaction = backend.query.get_transaction(self.connection, transaction_id)
        asset = backend.query.get_asset(self.connection, transaction_id)

        if transaction:
            if asset:
                transaction['asset'] = asset
            else:
                transaction['asset'] = {'data': None}

            transaction = Transaction.from_dict(transaction)

        if include_status:
            return transaction, self.TX_VALID if transaction else None
        else:
            return transaction

    def get_spent(self, txid, output):
        transaction = backend.query.get_spent(self.connection, txid,
                                              output)
        return Transaction.from_dict(transaction)

    def store_block(self, block):
        """Create a new block."""

        return backend.query.store_block(self.connection, block)

    def get_latest_block(self):
        """Get the block with largest height."""

        return backend.query.get_latest_block(self.connection)

    def validate_transaction(self, tx):
        """Validate a transaction against the current status of the database."""

        transaction = tx

        if not isinstance(transaction, Transaction):
            try:
                transaction = Transaction.from_dict(tx)
            except SchemaValidationError as e:
                logger.warning('Invalid transaction schema: %s', e.__cause__.message)
                return False
            except ValidationError as e:
                logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
                return False
        try:
            return transaction.validate(self)
        except ValidationError as e:
            logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
            return False
        return transaction


Block = namedtuple('Block', ('app_hash', 'height'))
