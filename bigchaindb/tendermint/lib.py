import logging

from bigchaindb import backend
from bigchaindb import Bigchain
from bigchaindb.models import Transaction
from bigchaindb.common.exceptions import SchemaValidationError, ValidationError


logger = logging.getLogger(__name__)


class BigchainDB(Bigchain):

    def write_transaction(self, transaction):
        """Write a valid transaction to the transactions collection."""

        return backend.query.write_transaction(self.connection, transaction.to_dict())

    def get_transaction(self, transaction, include_status=False):
        result = backend.query.get_transaction(self.connection, transaction)

        if result:
            result = Transaction.from_dict(result)

        if include_status:
            return result, self.TX_VALID if result else None
        else:
            return result

    def get_spent(self, txid, output):
        transaction = backend.query.get_spent(self.connection, txid, output)
        return Transaction.from_dict(transaction)

    def validate_transaction(self, tx):
        """Validate a transaction against the current status
        of the database."""

        try:
            tx_obj = Transaction.from_dict(tx)
        except SchemaValidationError as e:
            logger.warning('Invalid transaction schema: %s', e.__cause__.message)
            return False
        except ValidationError as e:
            logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
            return False

        try:
            return tx_obj.validate(self)
        except ValidationError as e:
            logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
            return False
        return tx_obj
