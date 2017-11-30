from copy import deepcopy
import pytest
import random

import bigchaindb
from bigchaindb.core import Bigchain
from contextlib import contextmanager
from bigchaindb.common.crypto import generate_key_pair
from tests.pipelines.stepping import create_stepper


################################################################################
# Test setup code


@contextmanager
def federation(n):
    """Return a list of Bigchain objects and pipeline steppers to represent
    a BigchainDB federation
    """
    keys = [generate_key_pair() for _ in range(n)]
    config_orig = bigchaindb.config

    @contextmanager
    def make_nodes(i):
        """make_nodes is a recursive context manager. Essentially it is doing:

        with f(a[0]) as b0:
            with f(a[1]) as b1:
                with f(a[2]) as b2:
                    yield [b0, b1, b2]

        with an arbitrary depth. It is also temporarily patching global
        configuration to simulate nodes with separate identities.
        """
        nonlocal keys
        if i == 0:
            yield []
        else:
            config = deepcopy(config_orig)
            keys = [keys[-1]] + keys[:-1]  # Rotate keys
            config['keyring'] = [pub for _, pub in keys[1:]]
            config['keypair']['private'] = keys[0][0]
            config['keypair']['public'] = keys[0][1]
            bigchaindb.config = config
            stepper = create_stepper()
            with stepper.start():
                node = (Bigchain(), stepper)
                with make_nodes(i-1) as rest:
                    yield [node] + rest

    with make_nodes(n) as steppers:
        bigchaindb.config = config_orig
        yield zip(*steppers)


@pytest.fixture
def federation_3():
    with federation(3) as f:
        yield f


def process_tx(steps):
    steps.block_changefeed(timeout=1)
    if steps.block_filter_tx():
        steps.block_validate_tx()
        steps.block_create(timeout=True)
        steps.block_write()
        steps.block_delete_tx()


def input_single_create(b):
    from bigchaindb.common.transaction import Transaction
    metadata = {'r': random.random()}
    tx = Transaction.create([b.me], [([b.me], 1)], metadata).sign([b.me_private])
    b.write_transaction(tx)
    return tx


def process_vote(steps, result=None):
    steps.vote_changefeed()
    steps.vote_validate_block()
    steps.vote_ungroup()
    steps.vote_validate_tx()
    if result is not None:
        steps.queues['vote_vote'][0][0] = result
    vote = steps.vote_vote()
    steps.vote_write_vote()
    return vote


################################################################################
# Tests here on down


@pytest.mark.bdb
@pytest.mark.genesis
@pytest.mark.skip_travis_rdb
def test_elect_valid(federation_3):
    [bx, (s0, s1, s2)] = federation_3
    tx = input_single_create(bx[0])
    process_tx(s0)
    process_tx(s1)
    process_tx(s2)
    process_vote(s2, False)
    for i in range(3):
        assert bx[i].get_transaction(tx.id, True)[1] == 'undecided'
    process_vote(s0, True)
    for i in range(3):
        assert bx[i].get_transaction(tx.id, True)[1] == 'undecided'
    process_vote(s1, True)
    for i in range(3):
        assert bx[i].get_transaction(tx.id, True)[1] == 'valid'


@pytest.mark.bdb
@pytest.mark.genesis
@pytest.mark.skip_travis_rdb
def test_elect_invalid(federation_3):
    [bx, (s0, s1, s2)] = federation_3
    tx = input_single_create(bx[0])
    process_tx(s0)
    process_tx(s1)
    process_tx(s2)
    process_vote(s1, True)
    for i in range(3):
        assert bx[i].get_transaction(tx.id, True)[1] == 'undecided'
    process_vote(s2, False)
    for i in range(3):
        assert bx[i].get_transaction(tx.id, True)[1] == 'undecided'
    process_vote(s0, False)
    for i in range(3):
        assert bx[i].get_transaction(tx.id, True)[1] is None


@pytest.mark.bdb
@pytest.mark.genesis
@pytest.mark.skip_travis_rdb
def test_elect_sybill(federation_3):
    [bx, (s0, s1, s2)] = federation_3
    tx = input_single_create(bx[0])
    process_tx(s0)
    process_tx(s1)
    process_tx(s2)
    # What we need is some votes from unknown nodes!
    # Incorrectly signed votes are ineligible.
    for s in [s0, s1, s2]:
        s.vote.bigchain.me_private = generate_key_pair()[0]
    process_vote(s0, True)
    process_vote(s1, True)
    process_vote(s2, True)
    for i in range(3):
        assert bx[i].get_transaction(tx.id, True)[1] == 'undecided'


@pytest.mark.skip()
@pytest.mark.bdb
@pytest.mark.genesis
def test_elect_dos(federation_3):
    """https://github.com/bigchaindb/bigchaindb/issues/1314
    Test that a node cannot block another node's opportunity to vote
    on a block by writing an incorrectly signed vote
    """
    raise NotImplementedError()


@pytest.mark.skip('Revisit when we have block election status cache')
@pytest.mark.bdb
@pytest.mark.genesis
def test_elect_bad_block_voters_list(federation_3):
    """See https://github.com/bigchaindb/bigchaindb/issues/1224"""
    [bx, (s0, s1, s2)] = federation_3
    b = s0.block.bigchain
    # First remove other nodes from node 0 so that it self assigns the tx
    b.nodes_except_me = []
    tx = input_single_create(b)
    # Now create a block voters list which will not match other keyrings
    b.nodes_except_me = [bx[1].me]
    process_tx(s0)
    process_vote(s0)
    process_vote(s1)
    process_vote(s2)
    for i in range(3):
        assert bx[i].get_transaction(tx.id, True)[1] == 'invalid'
