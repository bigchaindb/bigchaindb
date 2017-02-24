import pytest

from bigchaindb.backend.exceptions import BigchainDBCritical
from bigchaindb.core import Bigchain
from bigchaindb.voting import Voting, INVALID, VALID, UNDECIDED


################################################################################
# Tests for checking vote eligibility


def test_partition_eligible_votes():
    class TestVoting(Voting):
        @classmethod
        def verify_vote_signature(cls, vote):
            if vote['node_pubkey'] == 'invalid sig':
                return False
            if vote['node_pubkey'] == 'value error':
                raise ValueError()
            return True

    voters = ['valid', 'invalid sig', 'value error', 'not in set']
    votes = [{'node_pubkey': k} for k in voters]

    el, inel = TestVoting.partition_eligible_votes(votes, voters[:-1])
    assert el == [votes[0]]
    assert inel == votes[1:]


################################################################################
# Test vote counting


def test_count_votes():
    class TestVoting(Voting):
        @classmethod
        def verify_vote_schema(cls, vote):
            return vote['node_pubkey'] != 'malformed'

    voters = ['cheat', 'cheat', 'says invalid', 'malformed']
    voters += ['kosher' + str(i) for i in range(10)]

    votes = [Bigchain(v).vote('block', 'a', True) for v in voters]
    votes[2]['vote']['is_block_valid'] = False
    votes[-1]['vote']['previous_block'] = 'z'

    assert TestVoting.count_votes(votes) == {
        'counts': {
            'n_valid': 10,
            'n_invalid': 3,
            'n_agree_prev_block': 9
        },
        'cheat': [votes[:2]],
        'malformed': [votes[3]],
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
    with pytest.raises(BigchainDBCritical):
        Voting.decide_votes(n_voters=1, n_valid=2, n_invalid=0,
                            n_agree_prev_block=0)
    with pytest.raises(BigchainDBCritical):
        Voting.decide_votes(n_voters=1, n_valid=0, n_invalid=2,
                            n_agree_prev_block=0)
    with pytest.raises(BigchainDBCritical):
        Voting.decide_votes(n_voters=1, n_valid=0, n_invalid=0,
                            n_agree_prev_block=2)


################################################################################
# Tests for vote signature


def test_verify_vote_signature_passes(b):
    vote = b.vote('block', 'a', True)
    assert Voting.verify_vote_signature(vote)


def test_verify_vote_signature_fails(b):
    vote = b.vote('block', 'a', True)
    vote['signature'] = ''
    assert not Voting.verify_vote_signature(vote)


################################################################################
# Tests for vote schema


def test_verify_vote_schema(b):
    vote = b.vote('b' * 64, 'a' * 64, True)
    assert Voting.verify_vote_schema(vote)
    vote = b.vote('b', 'a', True)
    assert not Voting.verify_vote_schema(vote)


################################################################################
# block_election tests
# A more thorough test will follow  as part of #1217


def test_block_election(b):

    class TestVoting(Voting):
        @classmethod
        def verify_vote_signature(cls, vote):
            return True

        @classmethod
        def verify_vote_schema(cls, vote):
            return True

    keyring = 'abc'
    block = {'id': 'xyz', 'block': {'voters': 'ab'}}
    votes = [{
        'node_pubkey': c,
        'vote': {'is_block_valid': True, 'previous_block': 'a'}
    } for c in 'abc']

    assert TestVoting.block_election(block, votes, keyring) == {
        'status': VALID,
        'block_id': 'xyz',
        'counts': {'n_agree_prev_block': 2, 'n_valid': 2, 'n_invalid': 0},
        'ineligible': [votes[-1]],
        'cheat': [],
        'malformed': [],
    }
