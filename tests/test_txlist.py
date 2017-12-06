"""Test getting a list of transactions from the backend.

This test module defines it's own fixture which is used by all the tests.
"""
import pytest


@pytest.fixture
def txlist(b, user_pk, user2_pk, user_sk, user2_sk, genesis_block):
    from bigchaindb.models import Transaction
    prev_block_id = genesis_block.id

    # Create first block with CREATE transactions
    create1 = Transaction.create([user_pk], [([user2_pk], 6)]) \
        .sign([user_sk])
    create2 = Transaction.create([user2_pk],
                                 [([user2_pk], 5), ([user_pk], 5)]) \
                         .sign([user2_sk])
    block1 = b.create_block([create1, create2])
    b.write_block(block1)

    # Create second block with TRANSFER transactions
    transfer1 = Transaction.transfer(create1.to_inputs(),
                                     [([user_pk], 8)],
                                     create1.id).sign([user2_sk])
    block2 = b.create_block([transfer1])
    b.write_block(block2)

    # Create block with double spend
    tx_doublespend = Transaction.transfer(create1.to_inputs(), [([user_pk], 9)],
                                          create1.id).sign([user2_sk])
    block_doublespend = b.create_block([tx_doublespend])
    b.write_block(block_doublespend)

    # Vote on all the blocks
    prev_block_id = genesis_block.id
    for bid in [block1.id, block2.id]:
        vote = b.vote(bid, prev_block_id, True)
        prev_block_id = bid
        b.write_vote(vote)

    # Create undecided block
    untx = Transaction.create([user_pk], [([user2_pk], 7)]) \
        .sign([user_sk])
    block_undecided = b.create_block([untx])
    b.write_block(block_undecided)

    return type('', (), {
        'create1': create1,
        'transfer1': transfer1,
    })


@pytest.mark.bdb
def test_get_txlist_by_asset(b, txlist):
    res = b.get_transactions_filtered(txlist.create1.id)
    assert set(tx.id for tx in res) == set([txlist.transfer1.id,
                                            txlist.create1.id])


@pytest.mark.bdb
def test_get_txlist_by_operation(b, txlist):
    res = b.get_transactions_filtered(txlist.create1.id, operation='CREATE')
    assert set(tx.id for tx in res) == {txlist.create1.id}
