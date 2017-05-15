import pytest
from unittest.mock import patch
import random


pytestmark = [pytest.mark.bdb]


@pytest.fixture
def dog(b, changing_timestamps, genesis_block, watchdog):
    return watchdog


def create_tx(b):
    from bigchaindb.common.transaction import Transaction
    metadata = {'r': random.random()}
    return (Transaction.create([b.me], [([b.me], 1)], metadata)
                       .sign([b.me_private]))


def transfer_tx(b, txs):
    from bigchaindb.common.transaction import Transaction
    metadata = {'r': random.random()}
    txin = txs[0]
    tx = Transaction.transfer(txin.to_inputs(), [([b.me], 1)],
                              asset_id=txin.id, metadata=metadata)
    return tx.sign([b.me_private])


def write_block(b, txs):
    block = b.create_block(txs)
    b.write_block(block)
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)
    return block


def test_block_election_status_change(b, dog):
    block = write_block(b, [create_tx(b)])
    # Create a second vote
    vote = b.vote(block.id, 'fake', True)
    assert dog.join() is None
    b.write_vote(vote)
    with patch.object(dog, 'b') as b_:
        b_.block_election_status.return_value = 'invalid'
        assert dog.join() == ('BLOCK ELECTION STATUS CHANGE', block.id)


def test_double_spend_single_block(b, dog):
    tx_create = create_tx(b)
    write_block(b, [tx_create])
    tx_transfer0 = transfer_tx(b, [tx_create])
    tx_transfer1 = transfer_tx(b, [tx_create])
    block = write_block(b, [tx_transfer0, tx_transfer1])
    assert dog.join() == ('DOUBLE SPEND SINGLE BLOCK', block.id)


def test_double_spend_across_blocks(b, dog):
    tx_create = create_tx(b)
    write_block(b, [tx_create])
    write_block(b, [transfer_tx(b, [tx_create])])
    block = write_block(b, [transfer_tx(b, [tx_create])])
    assert dog.join() == ('DOUBLE SPEND ACROSS BLOCKS', block.id)


def test_duplicate_tx_single_block(b, dog):
    tx_create = create_tx(b)
    block = write_block(b, [tx_create, tx_create])
    assert dog.join() == ('DUPLICATE TX SINGLE BLOCK', block.id)


def test_duplicate_tx_different_block(b, dog):
    tx_create = create_tx(b)
    write_block(b, [tx_create])
    block = write_block(b, [tx_create])
    assert dog.join() == ('DUPLICATE TX ACROSS BLOCKS', block.id)


def test_input_does_not_exists(b, dog):
    tx_create = create_tx(b)
    write_block(b, [tx_create])
    tx_transfer = transfer_tx(b, [tx_create])
    tx_transfer.inputs[0].fulfills.txid = 'nop'
    block = write_block(b, [tx_transfer])
    assert dog.join() == ('INPUT DOES NOT EXIST', block.id)


def test_tx_balance_error(b, dog):
    tx_create = create_tx(b)
    write_block(b, [tx_create])
    tx_transfer = transfer_tx(b, [tx_create])
    tx_transfer.outputs[0].amount = 2
    block = write_block(b, [tx_transfer])
    assert dog.join() == ('TX BALANCE ERROR', block.id)
