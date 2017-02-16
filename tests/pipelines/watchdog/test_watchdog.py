import pytest
import random
from bigchaindb import watchdog as dog

"""

Correctness assertions

Tx output spent only once (across one block or many blocks)
Tx appears only once (across one block or many blocks)
No structurally invalid Tx (schema, policy, sum of inputs == sum of outputs)
No Tx that spends non existing output
All fulfillments must contain signature
All signatures are verified using Tx identity and crypto-condition of output
Threshold and Ed25519 condition is supported (up to some size limit)
All Txes verifiable according to signatures and hash(serialize(tx))
Txes appear in dependency order which is a PARTIAL order
We are able to provide non embarrassing timestamp
"""

pytestmark = [pytest.mark.bdb]


@pytest.fixture
def ctx(b, changing_timestamps, genesis_block, watchdog):
    b.create_genesis_block
    return type('', (), {'watchdog': watchdog})()


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


def test_double_spend_across_blocks(b, ctx):
    tx_create = create_tx(b)
    write_block(b, [tx_create])
    write_block(b, [transfer_tx(b, [tx_create])])
    block = write_block(b, [transfer_tx(b, [tx_create])])
    assert ctx.watchdog.join() == ('DOUBLE SPEND ACROSS BLOCKS', block.id)


def test_double_spend_single_block(b, ctx):
    tx_create = create_tx(b)
    write_block(b, [tx_create])
    tx_transfer = transfer_tx(b, [tx_create])
    tx_transfer = transfer_tx(b, [tx_create])
    block = write_block(b, [tx_transfer, tx_transfer])
    assert ctx.watchdog.join() == ('DOUBLE SPEND SINGLE BLOCK', block.id)


def test_duplicate_tx_single_block(b, ctx):
    tx_create = create_tx(b)
    block = write_block(b, [tx_create, tx_create])
    assert ctx.watchdog.join() == ('DUPLICATE TX SINGLE BLOCK', block.id)


def test_duplicate_tx_different_block(b, ctx):
    tx_create = create_tx(b)
    write_block(b, [tx_create])
    block = write_block(b, [tx_create])
    assert ctx.watchdog.join() == ('DUPLICATE TX ACROSS BLOCKS', block.id)
