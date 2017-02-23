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
