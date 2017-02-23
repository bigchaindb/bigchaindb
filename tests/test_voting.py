import pytest
from unittest.mock import patch

from bigchaindb.core import Bigchain
from bigchaindb.voting import Voting, INVALID, VALID, UNDECIDED


################################################################################
# Tests for checking vote eligibility


@patch('bigchaindb.voting.Voting.verify_vote_signature')
def test_partition_eligible_votes(_):
    nodes = list(map(Bigchain, 'abc'))
    votes = [n.vote('block', 'a', True) for n in nodes]

    el, inel = Voting.partition_eligible_votes(votes, 'abc')

    assert el == votes
    assert inel == []


@patch('bigchaindb.voting.Voting.verify_vote_schema')
def test_count_votes(_):
    nodes = list(map(Bigchain, 'abc'))

    votes = [n.vote('block', 'a', True) for n in nodes]

    assert Voting.count_votes(votes)['counts'] == {
        'n_valid': 3,
        'n_invalid': 0,
        'n_agree_prev_block': 3
    }


################################################################################
# Tests for vote decision making


DECISION_TESTS = [dict(
    zip(['n_voters', 'n_valid', 'n_invalid', 'n_agree_prev_block'], t))
    for t in [
         (1,          1,         1,           1),
         (2,          2,         1,           2),
         (3,          2,         2,           2),
         (4,          3,         2,           3),
         (5,          3,         3,           3),
         (6,          4,         3,           4),
         (7,          4,         4,           4),
         (8,          5,         4,           5),
    ]
]


@pytest.mark.parametrize('kwargs', DECISION_TESTS)
def test_decide_votes_valid(kwargs):
    kwargs = kwargs.copy()
    kwargs['n_invalid'] = 0
    assert Voting.decide_votes(**kwargs) == VALID
    kwargs['n_agree_prev_block'] -= 1
    assert Voting.decide_votes(**kwargs) == INVALID
    kwargs['n_valid'] -= 1
    assert Voting.decide_votes(**kwargs) == UNDECIDED


@pytest.mark.parametrize('kwargs', DECISION_TESTS)
def test_decide_votes_invalid(kwargs):
    kwargs = kwargs.copy()
    kwargs['n_valid'] = 0
    assert Voting.decide_votes(**kwargs) == INVALID
    kwargs['n_invalid'] -= 1
    assert Voting.decide_votes(**kwargs) == UNDECIDED


def test_decide_votes_checks_arguments():
    with pytest.raises(ValueError):
        Voting.decide_votes(n_voters=1, n_valid=2, n_invalid=0,
                            n_agree_prev_block=0)
    with pytest.raises(ValueError):
        Voting.decide_votes(n_voters=1, n_valid=0, n_invalid=2,
                            n_agree_prev_block=0)
    with pytest.raises(ValueError):
        Voting.decide_votes(n_voters=1, n_valid=0, n_invalid=0,
                            n_agree_prev_block=2)



################################################################################

# DEBT



def _test_verify_vote_passes(b, structurally_valid_vote):
    from bigchaindb.consensus import BaseConsensusRules
    from bigchaindb.common import crypto
    from bigchaindb.common.utils import serialize
    vote_body = structurally_valid_vote['vote']
    vote_data = serialize(vote_body)
    signature = crypto.PrivateKey(b.me_private).sign(vote_data.encode())
    vote_signed = {
        'node_pubkey': b.me,
        'signature': signature.decode(),
        'vote': vote_body
    }
    assert BaseConsensusRules.verify_vote([b.me], vote_signed)


def _test_verify_vote_fails_signature(b, structurally_valid_vote):
    from bigchaindb.consensus import BaseConsensusRules
    vote_body = structurally_valid_vote['vote']
    vote_signed = {
        'node_pubkey': b.me,
        'signature': 'a' * 86,
        'vote': vote_body
    }
    assert not BaseConsensusRules.verify_vote([b.me], vote_signed)


def _test_verify_vote_fails_schema(b):
    from bigchaindb.consensus import BaseConsensusRules
    from bigchaindb.common import crypto
    from bigchaindb.common.utils import serialize
    vote_body = {}
    vote_data = serialize(vote_body)
    signature = crypto.PrivateKey(b.me_private).sign(vote_data.encode())
    vote_signed = {
        'node_pubkey': b.me,
        'signature': signature.decode(),
        'vote': vote_body
    }
    assert not BaseConsensusRules.verify_vote([b.me], vote_signed)


"""
    @pytest.mark.genesis
    def test_more_votes_than_voters(self, b):
        from bigchaindb.common.exceptions import MultipleVotesError

        block_1 = dummy_block()
        b.write_block(block_1)
        # insert duplicate votes
        vote_1 = b.vote(block_1.id, b.get_last_voted_block().id, True)
        vote_2 = b.vote(block_1.id, b.get_last_voted_block().id, True)
        vote_2['node_pubkey'] = 'aaaaaaa'
        b.write_vote(vote_1)
        b.write_vote(vote_2)

        with pytest.raises(MultipleVotesError) as excinfo:
            b.block_election_status(block_1.id, block_1.voters)
        assert excinfo.value.args[0] == 'Block {block_id} has {n_votes} votes cast, but only {n_voters} voters'\
            .format(block_id=block_1.id, n_votes=str(2), n_voters=str(1))

    def test_multiple_votes_single_node(self, b, genesis_block):
        from bigchaindb.common.exceptions import MultipleVotesError

        block_1 = dummy_block()
        b.write_block(block_1)
        # insert duplicate votes
        for i in range(2):
            b.write_vote(b.vote(block_1.id, genesis_block.id, True))

        with pytest.raises(MultipleVotesError) as excinfo:
            b.block_election_status(block_1.id, block_1.voters)
        assert excinfo.value.args[0] == 'Block {block_id} has multiple votes ({n_votes}) from voting node {node_id}'\
            .format(block_id=block_1.id, n_votes=str(2), node_id=b.me)

        with pytest.raises(MultipleVotesError) as excinfo:
            b.has_previous_vote(block_1.id)
        assert excinfo.value.args[0] == 'Block {block_id} has {n_votes} votes from public key {me}'\
            .format(block_id=block_1.id, n_votes=str(2), me=b.me)

"""
