import pytest
import random


@pytest.mark.bdb
@pytest.mark.genesis
def test_stepping_changefeed_produces_update(b, steps):
    tx = input_single_create(b)

    # timeouts are 0 so will reassign immediately
    steps.stale_check_transactions()
    steps.stale_reassign_transactions()

    # We expect 2 changefeed events
    steps.block_changefeed()
    steps.block_changefeed()

    assert steps.counts == {'block_filter_tx': 2}
    assert ([tx['id'] for (tx,) in steps.queues['block_filter_tx']] ==
            [tx.id, tx.id])


@pytest.mark.bdb
@pytest.mark.genesis
def test_dupe_tx_in_block(b, steps):
    tx = input_single_create(b)
    for i in range(2):
        steps.stale_check_transactions()
        steps.stale_reassign_transactions()
        steps.block_changefeed()
        steps.block_filter_tx()
    steps.block_validate_tx()
    steps.block_validate_tx()
    assert steps.counts == {'block_create': 2}
    steps.block_create(timeout=False)
    block = steps.block_create(timeout=True)
    assert block.transactions == [tx]


def input_single_create(b):
    from bigchaindb.common.transaction import Transaction
    metadata = {'r': random.random()}
    tx = Transaction.create([b.me], [([b.me], 1)], metadata).sign([b.me_private])
    b.write_transaction(tx)
    return tx
