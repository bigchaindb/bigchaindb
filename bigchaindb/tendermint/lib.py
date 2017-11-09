import logging
from uuid import uuid4

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
        """Submit a valid transaction to the mempool."""

        self.post_transaction(transaction)

    def store_transaction(self, transaction):
        """Store a valid transaction to the transactions collection."""

        return backend.query.store_transaction(self.connection, transaction.to_dict())

    def get_transaction(self, transaction, include_status=False):
        result = backend.query.get_transaction(self.connection, transaction)

        if result:
            result = Transaction.from_dict(result)

        if include_status:
            return result, self.TX_VALID if result else None
        else:
            return result

    def get_spent(self, txid, output):
        transaction = backend.query.get_spent(self.connection, txid,
                                              output)
        return Transaction.from_dict(transaction)

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
