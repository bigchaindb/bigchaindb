import pytest

from bigchaindb.common.transaction import TransactionLink
from bigchaindb.models import Block, Transaction

pytestmark = pytest.mark.bdb


@pytest.fixture
def blockdata(b, user_pk, user2_pk):
    txs = [Transaction.create([user_pk], [([user2_pk], 1)]),
           Transaction.create([user2_pk], [([user_pk], 1)]),
           Transaction.create([user_pk], [([user_pk], 1), ([user2_pk], 1)])]
    blocks = []
    for i in range(3):
        block = Block([txs[i]])
        b.write_block(block)
        blocks.append(block.to_dict())
        if i > 0:
            b.write_vote(b.vote(block.id, '', i % 2 == 1))
    return blocks, [b['id'] for b in blocks]


def test_filter_block_ids_with_undecided(b, blockdata):
    blocks, block_ids = blockdata
    valid_ids = b.fastquery.filter_block_ids(block_ids)
    assert set(valid_ids) == {blocks[0]['id'], blocks[1]['id']}


def test_filter_block_ids_only_valid(b, blockdata):
    blocks, block_ids = blockdata
    valid_ids = b.fastquery.filter_block_ids(block_ids, include_undecided=False)
    assert set(valid_ids) == {blocks[1]['id']}


def test_filter_valid_blocks(b, blockdata):
    blocks, _ = blockdata
    assert b.fastquery.filter_valid_blocks(blocks) == [blocks[0], blocks[1]]


def test_get_outputs_by_pubkey(b, user_pk, user2_pk, blockdata):
    blocks, _ = blockdata
    assert b.fastquery.get_outputs_by_pubkey(user_pk) == [
            TransactionLink(blocks[1]['block']['transactions'][0]['id'], 0)
    ]
    assert b.fastquery.get_outputs_by_pubkey(user2_pk) == [
            TransactionLink(blocks[0]['block']['transactions'][0]['id'], 0)
    ]


def test_filter_spent_outputs(b, user_pk):
    out = [([user_pk], 1)]
    tx1 = Transaction.create([user_pk], out * 3)
    inputs = tx1.to_inputs()
    tx2 = Transaction.transfer([inputs[0]], out, tx1.id)
    tx3 = Transaction.transfer([inputs[1]], out, tx1.id)
    tx4 = Transaction.transfer([inputs[2]], out, tx1.id)

    for tx in [tx1, tx2]:
        block = Block([tx])
        b.write_block(block)
        b.write_vote(b.vote(block.id, '', True))

    # mark invalid
    block = Block([tx3])
    b.write_block(block)
    b.write_vote(b.vote(block.id, '', False))

    # undecided
    block = Block([tx4])
    b.write_block(block)

    unspents = b.fastquery.filter_spent_outputs(
             b.fastquery.get_outputs_by_pubkey(user_pk))

    assert set(unspents) == {
        inputs[1].fulfills,
        tx2.to_inputs()[0].fulfills,
        tx4.to_inputs()[0].fulfills
    }
