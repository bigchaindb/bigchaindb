import pytest
from bigchaindb.watchdog import Watchdog


@pytest.mark.bdb
def test_watch(b):
    from bigchaindb.common.transaction import Transaction
    watch = Watchdog()
    watch.start()
    b.create_genesis_block()

    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])
    block1 = b.create_block([tx, tx])
    b.write_block(block1)

    transfer_tx = Transaction.transfer(tx.to_inputs(), [([b.me], 1)],
                                       asset_id=tx.id)
    transfer_tx = transfer_tx.sign([b.me_private])
    transfer_tx2 = Transaction.transfer(tx.to_inputs(), [([b.me], 2)],
                                        asset_id=tx.id)
    transfer_tx2 = transfer_tx2.sign([b.me_private])
    block2 = b.create_block([transfer_tx, transfer_tx2])
    #b.write_block(block2)


    vote = b.vote(block1.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    # Vote both block2 and block3 valid to provoke a double spend
    #vote = b.vote(block2.id, b.get_last_voted_block().id, True)
    #b.write_vote(vote)
    #vote = b.vote(block3.id, b.get_last_voted_block().id, True)
    #b.write_vote(vote)

    watch.join()
