import pytest
import random


@pytest.mark.bdb
def test_stepping_changefeed_produces_update(b, steps):
    input_single_create(b)
    steps.block_changefeed()
    steps.block_filter_tx()

    # timeouts are 0 so will reassign immediately
    steps.stale_check_transactions()
    steps.stale_reassign_transactions()

    # We expect 2 changefeed events
    steps.block_changefeed()
    steps.block_filter_tx()


def input_single_create(b):
    from bigchaindb.common.transaction import Transaction
    metadata = {'r': random.random()}
    tx = Transaction.create([b.me], [([b.me], 1)], metadata)
    b.write_transaction(tx)
