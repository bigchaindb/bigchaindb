from bigchaindb.models import Transaction
from bigchaindb.upsert_validator import ValidatorElection


OPERATION_TO_CLASS = {
    Transaction.CREATE: Transaction,
    Transaction.TRANSFER: Transaction,
    ValidatorElection.VALIDATOR_ELECTION: ValidatorElection
}


def operation_class(tx):
    """For the given `tx` based on the `operation` key return its implementation class"""

    if isinstance(tx, dict):
        return OPERATION_TO_CLASS.get(tx.get('operation', Transaction.CREATE), Transaction)
    else:
        return Transaction
