from bigchaindb import Bigchain
from bigchaindb.pipelines import stale
from multipipes import Pipe, Pipeline
from unittest.mock import patch
from bigchaindb import config_utils
import os


def test_get_stale(b, user_pk):
    from bigchaindb.models import Transaction
    tx = Transaction.create([b.me], [([user_pk], 1)])
    tx = tx.sign([b.me_private])
    b.write_transaction(tx, durability='hard')

    stm = stale.StaleTransactionMonitor(timeout=0.001,
                                        backlog_reassign_delay=0.001)
    tx_stale = stm.check_transactions()

    for _tx in tx_stale:
        _tx.pop('assignee')
        _tx.pop('assignment_timestamp')
        assert tx.to_dict() == _tx


def test_reassign_transactions(b, user_pk):
    from bigchaindb.backend import query
    from bigchaindb.models import Transaction
    # test with single node
    tx = Transaction.create([b.me], [([user_pk], 1)])
    tx = tx.sign([b.me_private])
    b.write_transaction(tx, durability='hard')

    stm = stale.StaleTransactionMonitor(timeout=0.001,
                                        backlog_reassign_delay=0.001)
    stm.reassign_transactions(tx.to_dict())

    # test with federation
    tx = Transaction.create([b.me], [([user_pk], 1)])
    tx = tx.sign([b.me_private])
    b.write_transaction(tx, durability='hard')

    stm = stale.StaleTransactionMonitor(timeout=0.001,
                                        backlog_reassign_delay=0.001)
    stm.bigchain.nodes_except_me = ['aaa', 'bbb', 'ccc']
    tx = list(query.get_stale_transactions(b.connection, 0))[0]
    stm.reassign_transactions(tx)

    reassigned_tx = list(query.get_stale_transactions(b.connection, 0))[0]
    assert reassigned_tx['assignment_timestamp'] > tx['assignment_timestamp']
    assert reassigned_tx['assignee'] != tx['assignee']

    # test with node not in federation
    tx = Transaction.create([b.me], [([user_pk], 1)])
    tx = tx.sign([b.me_private])
    stm.bigchain.nodes_except_me = ['lol']
    b.write_transaction(tx, durability='hard')
    stm.bigchain.nodes_except_me = None

    tx = list(query.get_stale_transactions(b.connection, 0))[0]
    stm.reassign_transactions(tx)
    assert tx['assignee'] != 'lol'


def test_full_pipeline(monkeypatch, user_pk):
    from bigchaindb.backend import query
    from bigchaindb.models import Transaction
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

    original_txs = {}
    original_txc = []

    monkeypatch.setattr('time.time', lambda: 1)

    for i in range(100):
        tx = Transaction.create([b.me], [([user_pk], 1)])
        tx = tx.sign([b.me_private])
        original_txc.append(tx.to_dict())

        b.write_transaction(tx)
    original_txs = list(query.get_stale_transactions(b.connection, 0))
    original_txs = {tx['id']: tx for tx in original_txs}

    assert len(original_txs) == 100

    monkeypatch.undo()

    inpipe = Pipe()
    # Each time the StaleTransactionMonitor pipeline runs, it reassigns
    # all eligible transactions. Passing this inpipe prevents that from
    # taking place more than once.
    inpipe.put(())
    outpipe = Pipe()
    pipeline = stale.create_pipeline(backlog_reassign_delay=1,
                                     timeout=1)
    pipeline.setup(indata=inpipe, outdata=outpipe)
    pipeline.start()

    # to terminate
    for _ in range(100):
        outpipe.get()

    pipeline.terminate()

    assert len(list(query.get_stale_transactions(b.connection, 0))) == 100
    reassigned_txs = list(query.get_stale_transactions(b.connection, 0))

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
