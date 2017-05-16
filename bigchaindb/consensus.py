from bigchaindb.common.asset.policy import validate_asset
from bigchaindb.voting import Voting


class BaseConsensusRules():
    """Base consensus rules for Bigchain.

    A consensus plugin must expose a class inheriting from this one via an entry_point.

    All methods listed below must be implemented.

    """
    voting = Voting

    @staticmethod
    def validate_transaction(bigchain, transaction):
        """See :meth:`bigchaindb.models.Transaction.validate`
        for documentation."""
        valid_tx = transaction.validate(bigchain)
        validate_asset(transaction, bigchain)
        return valid_tx

    @staticmethod
    def validate_block(bigchain, block):
        """See :meth:`bigchaindb.models.Block.validate` for documentation."""
        return block.validate(bigchain)
