import pytest
import random

################################################################################
# Test some basic assumption


@pytest.mark.bdb
@pytest.mark.genesis
def test_stepping_changefeed_produces_update(b, steps):
    tx = input_single_create(b)
    stale_reassign(steps)
    # We expect 2 changefeed events
    steps.block_changefeed()
    steps.block_changefeed()

    assert steps.counts == {'block_filter_tx': 2}
    assert ([tx['id'] for (tx,) in steps.queues['block_filter_tx']] ==
            [tx.id, tx.id])


################################################################################
# Tests related to double inclusion (not the same as double spend)


@pytest.mark.bdb
@pytest.mark.genesis
@pytest.mark.usefixtures('changing_timestamps')
def test_steps_double_CREATE_inclusion(b, steps, genesis_block):

    # Create two blocks containing the same TX, both are UNDECIDED
    tx = input_single_create(b)
    block_create_tx_from_changefeed(steps)
    stale_reassign(steps)
    block_create_tx_from_changefeed(steps)

    # Write and vote both blocks
    for i in range(2):
        steps.block_write()
        steps.block_delete_tx()
        vote_full(steps)

    assert steps.counts == {}

    statuses = b.get_blocks_status_containing_tx(tx.id)
    assert set(statuses.values()) == set([b.BLOCK_VALID, b.BLOCK_INVALID])


################################################################################
# Common functions


def input_single_create(b):
    from bigchaindb.common.transaction import Transaction
    metadata = {'r': random.random()}
    tx = (Transaction.create([b.me], [([b.me], 1)], metadata)
                     .sign([b.me_private]))
    b.write_transaction(tx)
    return tx


def stale_reassign(steps):
    # timeouts are 0 so will reassign immediately
    steps.stale_check_transactions()
    steps.stale_reassign_transactions()


def block_create_tx_from_changefeed(steps):
    steps.block_changefeed(timeout=0.1)
    steps.block_filter_tx()
    steps.block_validate_tx()
    steps.block_create(timeout=True)


def vote_full(steps):
    steps.vote_changefeed()
    steps.vote_validate_block()
    steps.vote_ungroup()
    steps.vote_validate_tx()
    steps.vote_vote()
    steps.vote_write_vote()
