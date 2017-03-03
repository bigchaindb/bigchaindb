import random
import time
from unittest.mock import patch

from multipipes import Pipe
import pytest


def test_filter_by_assignee(b, signed_create_tx):
    from bigchaindb.pipelines.block import BlockPipeline

    block_maker = BlockPipeline()

    tx = signed_create_tx.to_dict()
    tx.update({'assignee': b.me, 'assignment_timestamp': 111})

    # filter_tx has side effects on the `tx` instance by popping 'assignee'
    # and 'assignment_timestamp'
    filtered_tx = block_maker.filter_tx(tx)
    assert filtered_tx == tx
    assert 'assignee' not in filtered_tx
    assert 'assignment_timestamp' not in filtered_tx

    tx = signed_create_tx.to_dict()
    tx.update({'assignee': 'nobody'})

    assert block_maker.filter_tx(tx) is None


@pytest.mark.bdb
def test_validate_transaction(b, create_tx):
    from bigchaindb.pipelines.block import BlockPipeline

    block_maker = BlockPipeline()

    assert block_maker.validate_tx(create_tx.to_dict()) is None

    valid_tx = create_tx.sign([b.me_private])
    assert block_maker.validate_tx(valid_tx.to_dict()) == valid_tx


def test_validate_transaction_handles_exceptions(b, signed_create_tx):
    """
    This test makes sure that `BlockPipeline.validate_tx` handles possible
    exceptions from `Transaction.from_dict`.
    """
    from bigchaindb.pipelines.block import BlockPipeline
    block_maker = BlockPipeline()
    from bigchaindb.common.exceptions import ValidationError

    tx_dict = signed_create_tx.to_dict()

    with patch('bigchaindb.models.Transaction.validate') as validate:
        # Assert that validationerror gets caught
        validate.side_effect = ValidationError()
        assert block_maker.validate_tx(tx_dict) is None

        # Assert that another error doesnt
        validate.side_effect = IOError()
        with pytest.raises(IOError):
            block_maker.validate_tx(tx_dict)


def test_create_block(b, user_pk):
    from bigchaindb.models import Transaction
    from bigchaindb.pipelines.block import BlockPipeline

    block_maker = BlockPipeline()

    for _ in range(100):
        tx = Transaction.create([b.me], [([user_pk], 1)],
                                metadata={'msg': random.random()})
        tx = tx.sign([b.me_private])
        block_maker.create(tx)

    # force the output triggering a `timeout`
    block_doc = block_maker.create(None, timeout=True)

    assert len(block_doc.transactions) == 100


@pytest.mark.bdb
def test_write_block(b, user_pk):
    from bigchaindb.models import Block, Transaction
    from bigchaindb.pipelines.block import BlockPipeline

    block_maker = BlockPipeline()

    txs = []
    for _ in range(100):
        tx = Transaction.create([b.me], [([user_pk], 1)],
                                metadata={'msg': random.random()})
        tx = tx.sign([b.me_private])
        txs.append(tx)

    block_doc = b.create_block(txs)
    block_maker.write(block_doc)
    expected = b.get_block(block_doc.id)
    expected = Block.from_dict(expected)

    assert expected == block_doc


@pytest.mark.bdb
def test_duplicate_transaction(b, user_pk):
    from bigchaindb.models import Transaction
    from bigchaindb.pipelines import block
    block_maker = block.BlockPipeline()

    txs = []
    for _ in range(10):
        tx = Transaction.create([b.me], [([user_pk], 1)],
                                metadata={'msg': random.random()})
        tx = tx.sign([b.me_private])
        txs.append(tx)

    block_doc = b.create_block(txs)
    block_maker.write(block_doc)

    # block is in bigchain
    assert b.get_block(block_doc.id) == block_doc.to_dict()

    b.write_transaction(txs[0])

    # verify tx is in the backlog
    assert b.get_transaction(txs[0].id) is not None

    # try to validate a transaction that's already in the chain; should not
    # work
    assert block_maker.validate_tx(txs[0].to_dict()) is None

    # duplicate tx should be removed from backlog
    response, status = b.get_transaction(txs[0].id, include_status=True)
    assert status != b.TX_IN_BACKLOG


@pytest.mark.bdb
def test_delete_tx(b, user_pk):
    from bigchaindb.models import Transaction
    from bigchaindb.pipelines.block import BlockPipeline
    block_maker = BlockPipeline()
    for i in range(100):
        tx = Transaction.create([b.me], [([user_pk], 1)],
                                metadata={'msg': random.random()})
        tx = tx.sign([b.me_private])
        block_maker.create(tx)
        # make sure the tx appears in the backlog
        b.write_transaction(tx)

    # force the output triggering a `timeout`
    block_doc = block_maker.create(None, timeout=True)

    for tx in block_doc.to_dict()['block']['transactions']:
        returned_tx = b.get_transaction(tx['id']).to_dict()
        assert returned_tx == tx

    returned_block = block_maker.delete_tx(block_doc)

    assert returned_block == block_doc

    for tx in block_doc.to_dict()['block']['transactions']:
        returned_tx, status = b.get_transaction(tx['id'], include_status=True)
        assert status != b.TX_IN_BACKLOG


@patch('bigchaindb.pipelines.block.create_pipeline')
@pytest.mark.bdb
def test_start(create_pipeline):
    from bigchaindb.pipelines import block

    pipeline = block.start()
    assert create_pipeline.called
    assert create_pipeline.return_value.setup.called
    assert create_pipeline.return_value.start.called
    assert pipeline == create_pipeline.return_value


@pytest.mark.bdb
def test_full_pipeline(b, user_pk):
    from bigchaindb.models import Block, Transaction
    from bigchaindb.pipelines.block import create_pipeline

    outpipe = Pipe()

    pipeline = create_pipeline()
    pipeline.setup(outdata=outpipe)
    inpipe = pipeline.items[0]

    # include myself here, so that some tx are actually assigned to me
    b.nodes_except_me = [b.me, 'aaa', 'bbb', 'ccc']
    number_assigned_to_others = 0
    for i in range(100):
        tx = Transaction.create([b.me], [([user_pk], 1)],
                                metadata={'msg': random.random()})
        tx = tx.sign([b.me_private])

        tx = tx.to_dict()

        # simulate write_transaction
        tx['assignee'] = random.choice(b.nodes_except_me)
        if tx['assignee'] != b.me:
            number_assigned_to_others += 1
        tx['assignment_timestamp'] = time.time()
        inpipe.put(tx)

    assert inpipe.qsize() == 100

    pipeline.start()

    time.sleep(2)

    pipeline.terminate()
    block_doc = outpipe.get()
    chained_block = b.get_block(block_doc.id)
    chained_block = Block.from_dict(chained_block)

    block_len = len(block_doc.transactions)
    assert chained_block == block_doc
    assert number_assigned_to_others == 100 - block_len
