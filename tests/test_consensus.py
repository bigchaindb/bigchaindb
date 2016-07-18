import pytest


class TestBaseConsensusRules(object):

    def test_validate_transaction(self):
        from bigchaindb.consensus import BaseConsensusRules
        transaction = {
            'transaction': {
                'operation': None,
                'fulfillments': None,
            },
        }
        with pytest.raises(ValueError):
            BaseConsensusRules.validate_transaction(None, transaction)
