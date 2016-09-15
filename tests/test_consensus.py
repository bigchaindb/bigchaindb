import pytest


class TestBaseConsensusRules(object):

    def test_validate_transaction(b, self):
        from bigchaindb.consensus import BaseConsensusRules
        from bigchaindb.models import Transaction

        transaction = Transaction.create([b.me], [b.me])
        with pytest.raises(ValueError):
            BaseConsensusRules.validate_transaction(None, transaction)
