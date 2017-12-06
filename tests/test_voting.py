import pytest
from unittest.mock import patch
from collections import Counter

from bigchaindb.core import Bigchain
from bigchaindb.exceptions import CriticalDuplicateVote
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
# Actions - test state transitions


@pytest.mark.parametrize('n_voters', range(8))
def test_vote_actions(n_voters):
    """* Legal transitions are UNDECIDED -> [VALID|INVALID] only
    * Block is never left UNDECIDED after voting
    * Accomodates rogues on previous block / invalid schema
    """
    class TestVoting(Voting):
        @classmethod
        def verify_vote_schema(cls, vote):
            return type(vote['vote']['is_block_valid']) == bool

        @classmethod
        def verify_vote_signature(cls, vote):
            return True

    keyring = 'abcdefghijklmnopqrstuvwxyz'[:n_voters]
    block = {'id': 'block', 'block': {'voters': keyring}}
    state = UNDECIDED
    todo = [(state, [], [])]

    def branch(p, r):
        todo.append((state, votes, votes + [{
            'node_pubkey': keyring[len(votes)],
            'vote': {'previous_block': p, 'is_block_valid': r}
        }]))

    while todo:
        prev_state, prev_votes, votes = todo.pop(0)
        results = Counter(v['vote']['is_block_valid'] for v in votes)
        prev_blocks = Counter(v['vote']['previous_block'] for v in votes)
        majority = n_voters // 2 + 1
        honest = (len(votes) == majority and len(prev_blocks) == 1 and
                  not results['lol'] and len(results) == 1)
        closed = len(votes) == n_voters

        # Test legal transition
        if votes:
            state = TestVoting.block_election(block, votes, keyring)['status']
            assert prev_state in [state, UNDECIDED]

        # Test that decision has been reached
        if honest or closed:
            assert state != UNDECIDED or n_voters == 0

        if closed:
            continue

        # Can accomodate more votes, add them to the todo list.
        # This vote is the good case
        branch('A', True)
        # This vote disagrees on previous block
        branch('B', True)
        # This vote says the block is invalid
        branch('A', False)
        # This vote is invalid
        branch('A', 'lol')


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


################################################################################
# block_election tests


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
        'counts': {'n_valid': 2, 'n_invalid': 0},
        'ineligible': [votes[-1]],
        'malformed': [],
        'previous_block': 'a',
        'other_previous_block': {},
    }


@patch('bigchaindb.voting.Voting.verify_vote_signature', return_value=True)
def test_duplicate_vote_throws_critical_error(b):
    keyring = 'abc'
    block = {'id': 'xyz', 'block': {'voters': 'ab'}}
    votes = [{
        'node_pubkey': c,
        'vote': {'is_block_valid': True, 'previous_block': 'a'}
    } for c in 'aabc']
    with pytest.raises(CriticalDuplicateVote):
        Voting.block_election(block, votes, keyring)
