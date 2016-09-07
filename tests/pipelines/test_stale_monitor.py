import rethinkdb as r
from bigchaindb import Bigchain
from bigchaindb.pipelines import stale
from multipipes import Pipe, Pipeline
from unittest.mock import patch
from bigchaindb import config_utils
import time
import os


def test_get_stale(b, user_vk):
    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)
    b.write_transaction(tx, durability='hard')

    stm = stale.StaleTransactionMonitor(timeout=0.001,
                                        backlog_reassign_delay=0.001)
    tx_stale = stm.check_transactions()

    for _tx in tx_stale:
        _tx.pop('assignee')
        _tx.pop('assignment_timestamp')
        assert tx == _tx


def test_reassign_transactions(b, user_vk):
    # test with single node
    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)
    b.write_transaction(tx, durability='hard')

    stm = stale.StaleTransactionMonitor(timeout=0.001,
                                        backlog_reassign_delay=0.001)
    stm.reassign_transactions(tx)

    # test with federation
    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)
    b.write_transaction(tx, durability='hard')

    stm = stale.StaleTransactionMonitor(timeout=0.001,
                                        backlog_reassign_delay=0.001)
    stm.bigchain.nodes_except_me = ['aaa', 'bbb', 'ccc']
    tx = list(r.table('backlog').run(b.conn))[0]
    stm.reassign_transactions(tx)

    reassigned_tx = r.table('backlog').get(tx['id']).run(b.conn)
    assert reassigned_tx['assignment_timestamp'] > tx['assignment_timestamp']
    assert reassigned_tx['assignee'] != tx['assignee']

    # test with node not in federation
    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)
    tx.update({'assignee': 'lol'})
    tx.update({'assignment_timestamp': time.time()})
    r.table('backlog').insert(tx, durability='hard').run(b.conn)

    tx = list(r.table('backlog').run(b.conn))[0]
    stm.reassign_transactions(tx)
    assert r.table('backlog').get(tx['id']).run(b.conn)['assignee'] != 'lol'


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
        'backlog_reassign_delay': 0.01
    }
    config_utils.set_config(CONFIG)
    b = Bigchain()
    outpipe = Pipe()

    original_txs = {}

    for i in range(100):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx = b.sign_transaction(tx, b.me_private)

        b.write_transaction(tx)
        original_txs[tx['id']] = r.table('backlog').get(tx['id']).run(b.conn) 

    assert r.table('backlog').count().run(b.conn) == 100

    pipeline = stale.create_pipeline(backlog_reassign_delay=1,
                                     timeout=1)
    pipeline.setup(outdata=outpipe)
    pipeline.start()

    # timing should be careful -- test will fail if reassignment happens multiple times
    time.sleep(2)
    pipeline.terminate()

    # to terminate
    outpipe.get()

    assert r.table('backlog').count().run(b.conn) == 100
    reassigned_txs = list(r.table('backlog').run(b.conn))

    # check that every assignment timestamp has increased, and every tx has a new assignee
    for reassigned_tx in reassigned_txs:
        assert reassigned_tx['assignment_timestamp'] > original_txs[reassigned_tx['id']]['assignment_timestamp']
        assert reassigned_tx['assignee'] != original_txs[reassigned_tx['id']]['assignee']

@patch.object(Pipeline, 'start')
def test_start(mock_start):
    # TODO: `sta,e.start` is just a wrapper around `block.create_pipeline`,
    #       that is tested by `test_full_pipeline`.
    #       If anyone has better ideas on how to test this, please do a PR :)
    stale.start()
    mock_start.assert_called_with()
