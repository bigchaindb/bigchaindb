# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


class BaseValidationRules():
    """Base validation rules for BigchainDB.

    A validation plugin must expose a class inheriting from this one via an entry_point.

    All methods listed below must be implemented.
    """

    @staticmethod
    def validate_transaction(bigchaindb, transaction):
        """See :meth:`bigchaindb.models.Transaction.validate`
        for documentation.
        """
        return transaction.validate(bigchaindb)

    @staticmethod
    def validate_block(bigchaindb, block):
        """See :meth:`bigchaindb.models.Block.validate` for documentation."""
        return block.validate(bigchaindb)
