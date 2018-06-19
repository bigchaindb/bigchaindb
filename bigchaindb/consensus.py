

class BaseConsensusRules():
    """Base consensus rules for Bigchain.

    A consensus plugin must expose a class inheriting from this one via an entry_point.

    All methods listed below must be implemented.

    """

    @staticmethod
    def validate_transaction(bigchain, transaction):
        """See :meth:`bigchaindb.models.Transaction.validate`
        for documentation.
        """
        return transaction.validate(bigchain)

    @staticmethod
    def validate_block(bigchain, block):
        """See :meth:`bigchaindb.models.Block.validate` for documentation."""
        return block.validate(bigchain)
