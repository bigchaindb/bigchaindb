import time
from unittest.mock import patch

import rethinkdb as r

from bigchaindb.pipelines import block
from multipipes import Pipe, Pipeline


def test_filter_by_assignee(b, signed_create_tx):
    block_maker = block.Block()

    tx = signed_create_tx.to_dict()
    tx.update({'assignee': b.me})

    # filter_tx has side effects on the `tx` instance by popping 'assignee'
    assert block_maker.filter_tx(tx) == tx

    tx = signed_create_tx.to_dict()
    tx.update({'assignee': 'nobody'})

    assert block_maker.filter_tx(tx) is None


def test_validate_transaction(b, signed_create_tx):
    block_maker = block.Block()

    tx = signed_create_tx.to_dict()
    tx['id'] = 'a' * 64

    assert block_maker.validate_tx(tx) is None

    valid_tx = signed_create_tx.to_dict()
    assert block_maker.validate_tx(valid_tx) == signed_create_tx


def test_create_block(b, user_vk):
    from bigchaindb_common.transaction import Transaction

    block_maker = block.Block()

    for i in range(100):
        tx = Transaction.create([b.me], [user_vk])
        tx = tx.sign([b.me_private])
        block_maker.create(tx)

    # force the output triggering a `timeout`
    block_doc = block_maker.create(None, timeout=True)

    assert len(block_doc['block']['transactions']) == 100


def test_write_block(b, user_vk):
    # TODO: Write Block class
    from bigchaindb.util import _serialize_txs_block
    from bigchaindb_common.transaction import Transaction

    block_maker = block.Block()

    txs = []
    for i in range(100):
        tx = Transaction.create([b.me], [user_vk])
        tx = tx.sign([b.me_private])
        txs.append(tx)

    block_doc = b.create_block(txs)
    block_maker.write(block_doc)
    expected = r.table('bigchain').get(block_doc['id']).run(b.conn)

    assert expected == _serialize_txs_block(block_doc)


def test_delete_tx(b, user_vk):
    from bigchaindb_common.transaction import Transaction

    block_maker = block.Block()

    tx = Transaction.create([b.me], [user_vk])
    tx = tx.sign([b.me_private])
    b.write_transaction(tx)

    backlog_tx = r.table('backlog').get(tx.id).run(b.conn)
    backlog_tx.pop('assignee')
    assert backlog_tx == tx.to_dict()

    returned_tx = block_maker.delete_tx(tx.to_dict())

    assert returned_tx == tx.to_dict()
    assert r.table('backlog').get(tx.id).run(b.conn) is None


def test_prefeed(b, user_vk):
    import random
    from bigchaindb_common.transaction import Transaction

    for i in range(100):
        tx = Transaction.create([b.me], [user_vk], {'msg': random.random()})
        tx = tx.sign([b.me_private])
        b.write_transaction(tx)

    backlog = block.initial()

    assert len(list(backlog)) == 100


@patch.object(Pipeline, 'start')
def test_start(mock_start):
    # TODO: `block.start` is just a wrapper around `block.create_pipeline`,
    #       that is tested by `test_full_pipeline`.
    #       If anyone has better ideas on how to test this, please do a PR :)
    block.start()
    mock_start.assert_called_with()


def test_full_pipeline(b, user_vk):
    import random
    # TODO: Create block model
    from bigchaindb.util import _serialize_txs_block
    from bigchaindb_common.transaction import Transaction

    outpipe = Pipe()

    count_assigned_to_me = 0
    for i in range(100):
        tx = Transaction.create([b.me], [user_vk], {'msg': random.random()})
        tx = tx.sign([b.me_private]).to_dict()
        assignee = random.choice([b.me, 'aaa', 'bbb', 'ccc'])
        tx['assignee'] = assignee
        if assignee == b.me:
            count_assigned_to_me += 1
        r.table('backlog').insert(tx, durability='hard').run(b.conn)

    assert r.table('backlog').count().run(b.conn) == 100

    pipeline = block.create_pipeline()
    pipeline.setup(indata=block.get_changefeed(), outdata=outpipe)
    pipeline.start()

    time.sleep(2)
    pipeline.terminate()

    block_doc = outpipe.get()
    chained_block = r.table('bigchain').get(block_doc['id']).run(b.conn)

    assert len(block_doc['block']['transactions']) == count_assigned_to_me
    assert chained_block == _serialize_txs_block(block_doc)
    assert r.table('backlog').count().run(b.conn) == 100 - count_assigned_to_me
