import time

import pytest


@pytest.mark.usefixtures('processes')
def test_fast_double_create(b, user_pk):
    from bigchaindb.models import Transaction
    from bigchaindb.backend.query import count_blocks
    tx = Transaction.create([b.me], [([user_pk], 1)],
                            metadata={'test': 'test'}).sign([b.me_private])

    # write everything fast
    b.write_transaction(tx)
    b.write_transaction(tx)

    time.sleep(2)
    tx_returned = b.get_transaction(tx.id)

    # test that the tx can be queried
    assert tx_returned == tx
    # test the transaction appears only once
    last_voted_block = b.get_last_voted_block()
    assert len(last_voted_block.transactions) == 1
    assert count_blocks(b.connection) == 2


@pytest.mark.usefixtures('processes')
def test_double_create(b, user_pk):
    from bigchaindb.models import Transaction
    from bigchaindb.backend.query import count_blocks
    tx = Transaction.create([b.me], [([user_pk], 1)],
                            metadata={'test': 'test'}).sign([b.me_private])

    b.write_transaction(tx)
    time.sleep(2)
    b.write_transaction(tx)
    time.sleep(2)
    tx_returned = b.get_transaction(tx.id)

    # test that the tx can be queried
    assert tx_returned == tx
    # test the transaction appears only once
    last_voted_block = b.get_last_voted_block()
    assert len(last_voted_block.transactions) == 1
    assert count_blocks(b.connection) == 2
