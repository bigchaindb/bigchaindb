import logging

from bigchaindb.models import Transaction
from bigchaindb.common.exceptions import SchemaValidationError, ValidationError


logger = logging.getLogger(__name__)


def validate_transaction(bigchaindb, tx):
    try:
        tx_obj = Transaction.from_dict(tx)
    except SchemaValidationError as e:
        logger.warning('Invalid transaction schema: %s', e.__cause__.message)
        return False
    except ValidationError as e:
        logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
        return False

    try:
        bigchaindb.validate_transaction(tx_obj)
    except ValidationError as e:
        logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
        return False
    return tx_obj


def write_transaction(bigchaindb, tx_obj):
    bigchaindb.write_transaction(tx_obj)
