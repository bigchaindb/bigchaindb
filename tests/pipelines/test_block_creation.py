import time
import random
from unittest.mock import patch

import rethinkdb as r

from bigchaindb.pipelines import block
from multipipes import Pipe, Pipeline


def test_filter_by_assignee(b, user_vk):
    block_maker = block.Block()

    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)
    tx['assignee'] = b.me

    # filter_tx has side effects on the `tx` instance by popping 'assignee'
    assert block_maker.filter_tx(tx) == tx

    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)
    tx['assignee'] = 'nobody'

    assert block_maker.filter_tx(tx) is None


def test_validate_transaction(b, user_vk):
    block_maker = block.Block()

    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)
    tx['id'] = 'a' * 64

    assert block_maker.validate_tx(tx) is None

    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)

    assert block_maker.validate_tx(tx) == tx


def test_create_block(b, user_vk):
    block_maker = block.Block()

    for i in range(100):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx = b.sign_transaction(tx, b.me_private)
        block_maker.create(tx)

    # force the output triggering a `timeout`
    block_doc = block_maker.create(None, timeout=True)

    assert len(block_doc['block']['transactions']) == 100


def test_write_block(b, user_vk):
    block_maker = block.Block()

    txs = []
    for i in range(100):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx = b.sign_transaction(tx, b.me_private)
        txs.append(tx)

    block_doc = b.create_block(txs)
    block_maker.write(block_doc)

    assert r.table('bigchain').get(block_doc['id']).run(b.conn) == block_doc


def test_delete_tx(b, user_vk):
    block_maker = block.Block()

    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)
    b.write_transaction(tx)

    tx_backlog = r.table('backlog').get(tx['id']).run(b.conn)
    tx_backlog.pop('assignee')
    assert tx_backlog == tx

    returned_tx = block_maker.delete_tx(tx)

    assert returned_tx == tx
    assert r.table('backlog').get(tx['id']).run(b.conn) is None


def test_prefeed(b, user_vk):
    for i in range(100):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx = b.sign_transaction(tx, b.me_private)
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
    outpipe = Pipe()

    count_assigned_to_me = 0
    for i in range(100):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx = b.sign_transaction(tx, b.me_private)
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

    assert len(block_doc['block']['transactions']) == count_assigned_to_me
    assert r.table('bigchain').get(block_doc['id']).run(b.conn) == block_doc
    assert r.table('backlog').count().run(b.conn) == 100 - count_assigned_to_me

