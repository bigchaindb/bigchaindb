import pytest

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

    voters = (['says invalid', 'malformed'] +
              ['kosher' + str(i) for i in range(10)])

    votes = [Bigchain(v).vote('block', 'a', True) for v in voters]
    votes[0]['vote']['is_block_valid'] = False
    # Incorrect previous block subtracts from n_valid and adds to n_invalid
    votes[-1]['vote']['previous_block'] = 'z'

    by_voter = dict(enumerate(votes))

    assert TestVoting.count_votes(by_voter) == {
        'counts': {
            'n_valid': 9,    # 9 kosher votes
            'n_invalid': 3,  # 1 invalid, 1 malformed, 1 rogue prev block
        },
        'malformed': [votes[1]],
        'previous_block': 'a',
        'other_previous_block': {'z': 1},
    }


def test_must_agree_prev_block():
    class TestVoting(Voting):
        @classmethod
        def verify_vote_schema(cls, vote):
            return True

    voters = 'abcd'
    votes = [Bigchain(v).vote('block', 'a', True) for v in voters]
    votes[0]['vote']['previous_block'] = 'b'
    votes[1]['vote']['previous_block'] = 'c'
    by_voter = dict(enumerate(votes))
    assert TestVoting.count_votes(by_voter) == {
        'counts': {
            'n_valid': 2,
            'n_invalid': 2,
        },
        'previous_block': 'a',
        'other_previous_block': {'b': 1, 'c': 1},
        'malformed': [],
    }


################################################################################
# Tests for vote decision making


DECISION_TESTS = [
    {'n_voters': 1, 'n_valid': 1, 'n_invalid': 1},
    {'n_voters': 2, 'n_valid': 2, 'n_invalid': 1},
    {'n_voters': 3, 'n_valid': 2, 'n_invalid': 2},
    {'n_voters': 4, 'n_valid': 3, 'n_invalid': 2},
    {'n_voters': 5, 'n_valid': 3, 'n_invalid': 3},
    {'n_voters': 6, 'n_valid': 4, 'n_invalid': 3},
    {'n_voters': 7, 'n_valid': 4, 'n_invalid': 4},
    {'n_voters': 8, 'n_valid': 5, 'n_invalid': 4}
]


@pytest.mark.parametrize('kwargs', DECISION_TESTS)
def test_decide_votes_valid(kwargs):
    kwargs = kwargs.copy()
    kwargs['n_invalid'] = 0
    assert Voting.decide_votes(**kwargs) == VALID
    kwargs['n_valid'] -= 1
    assert Voting.decide_votes(**kwargs) == UNDECIDED


@pytest.mark.parametrize('kwargs', DECISION_TESTS)
def test_decide_votes_invalid(kwargs):
    kwargs = kwargs.copy()
    kwargs['n_valid'] = 0
    assert Voting.decide_votes(**kwargs) == INVALID
    kwargs['n_invalid'] -= 1
    assert Voting.decide_votes(**kwargs) == UNDECIDED


################################################################################
# Tests for vote signature


def test_verify_vote_signature_passes(b):
    vote = b.vote('block', 'a', True)
    assert Voting.verify_vote_signature(vote)
    vote['signature'] = ''
    assert not Voting.verify_vote_signature(vote)


################################################################################
# Tests for vote schema


def test_verify_vote_schema(b):
    vote = b.vote('b' * 64, 'a' * 64, True)
    assert Voting.verify_vote_schema(vote)
    vote = b.vote('b' * 64, 'a', True)
    assert not Voting.verify_vote_schema(vote)
    vote = b.vote('b', 'a' * 64, True)
    assert not Voting.verify_vote_schema(vote)
