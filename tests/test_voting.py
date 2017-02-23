import pytest

from bigchaindb.core import Bigchain
from bigchaindb.voting import (count_votes, partition_eligible_votes,
                               decide_votes, INVALID, VALID, UNDECIDED)


def test_partition_eligible_votes():
    nodes = list(map(Bigchain, 'abc'))
    votes = [n.vote('block', 'a', True) for n in nodes]

    el, inel = partition_eligible_votes(votes, 'abc', lambda _: True)

    assert el == votes
    assert inel == []


def test_count_votes():
    nodes = list(map(Bigchain, 'abc'))
    votes = [n.vote('block', 'a', True) for n in nodes]

    assert count_votes(votes) == ({
        'n_valid': 3,
        'n_invalid': 0,
        'n_agree_prev_block': 3
    }, {})


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
    assert decide_votes(**kwargs) == VALID
    kwargs['n_agree_prev_block'] -= 1
    assert decide_votes(**kwargs) == INVALID
    kwargs['n_valid'] -= 1
    assert decide_votes(**kwargs) == UNDECIDED


@pytest.mark.parametrize('kwargs', DECISION_TESTS)
def test_decide_votes_invalid(kwargs):
    kwargs = kwargs.copy()
    kwargs['n_valid'] = 0
    assert decide_votes(**kwargs) == INVALID
    kwargs['n_invalid'] -= 1
    assert decide_votes(**kwargs) == UNDECIDED
