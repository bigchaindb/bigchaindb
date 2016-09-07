import rethinkdb as r
from bigchaindb import Bigchain
from bigchaindb.pipelines import stale
from multipipes import Pipe, Pipeline
from unittest.mock import patch
from bigchaindb import config_utils
import random
import time
import os


def test_get_stale(b, user_vk):
    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)
    b.write_transaction(tx, durability='hard')

    stm = stale.StaleTransactionMonitor(backlog_reassign_delay=0.001)
    tx_stale = stm.check_transactions()

    assert len(tx_stale) == 1
    assert tx == tx_stale[0]


def test_reassign_transactions(b, user_vk):
    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)
    b.write_transaction(tx, durability='hard')

    stm = stale.StaleTransactionMonitor(backlog_reassign_delay=0.001)
    stm.bigchain.nodes_except_me = ['aaa', 'bbb', 'ccc']
    stm.reassign_transactions([tx])

    assert r.table('backlog').count().run(b.conn) == 1
    reassigned_tx = list(r.table('backlog').run(b.conn))[0]
    assert reassigned_tx['assignment_timestamp'] > tx['assignment_timestamp']
    assert reassigned_tx['assignee'] != tx['assignee']


def test_full_pipeline(user_vk):
    CONFIG = {
        'database': {
            'name': 'bigchain_test_{}'.format(os.getpid())
        },
        'keypair': {
            'private': '31Lb1ZGKTyHnmVK3LUMrAUrPNfd4sE2YyBt3UA4A25aA',
            'public': '4XYfCbabAWVUCbjTmRTFEu2sc3dFEdkse4r6X498B1s8'
        },
        'keyring': ['aaa', 'bbb'],
        'backlog_reassign_delay': 1
    }
    config_utils.set_config(CONFIG)
    b = Bigchain()
    outpipe = Pipe()

    original_txs = {}
    count_assigned_to_me = 0
    for i in range(100):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx = b.sign_transaction(tx, b.me_private)

        b.write_transaction(tx)
        original_txs[tx['id']] = tx

    assert r.table('backlog').count().run(b.conn) == 100

    pipeline = stale.create_pipeline(timeout=1)
    pipeline.setup(outdata=outpipe)
    pipeline.start()

    time.sleep(2)
    pipeline.terminate()

    # to terminate
    outpipe.get()

    assert r.table('backlog').count().run(b.conn) == 100
    reassigned_txs = list(r.table('backlog').run(b.conn))
    for reassigned_tx in reassigned_txs:
        assert reassigned_tx['assignee'] != original_txs[reassigned_tx['id']]['assignee']