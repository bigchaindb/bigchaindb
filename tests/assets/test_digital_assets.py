import pytest
import random


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_asset_transfer(b, user_pk, user_sk):
    from bigchaindb.models import Transaction

    tx_input = b.get_owned_ids(user_pk).pop()
    tx_create = b.get_transaction(tx_input.txid)

    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([user_pk], 1)],
                                       tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert tx_transfer_signed.asset['id'] == tx_create.id


def test_validate_bad_asset_creation(b, user_pk):
    from bigchaindb.models import Transaction

    # `data` needs to be a dictionary
    tx = Transaction.create([b.me], [([user_pk], 1)])
    tx.asset['data'] = 'a'
    tx_signed = tx.sign([b.me_private])

    with pytest.raises(TypeError):
        b.validate_transaction(tx_signed)


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_validate_transfer_asset_id_mismatch(b, user_pk, user_sk):
    from bigchaindb.common.exceptions import AssetIdMismatch
    from bigchaindb.models import Transaction

    tx_create = b.get_owned_ids(user_pk).pop()
    tx_create = b.get_transaction(tx_create.txid)
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([user_pk], 1)],
                                       tx_create.id)
    tx_transfer.asset['id'] = 'aaa'
    tx_transfer_signed = tx_transfer.sign([user_sk])
    with pytest.raises(AssetIdMismatch):
        tx_transfer_signed.validate(b)


def test_get_asset_id_create_transaction(b, user_pk):
    from bigchaindb.models import Transaction

    tx_create = Transaction.create([b.me], [([user_pk], 1)])
    asset_id = Transaction.get_asset_id(tx_create)

    assert asset_id == tx_create.id


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_asset_id_transfer_transaction(b, user_pk, user_sk):
    from bigchaindb.models import Transaction

    tx_create = b.get_owned_ids(user_pk).pop()
    tx_create = b.get_transaction(tx_create.txid)
    # create a transfer transaction
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([user_pk], 1)],
                                       tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])
    # create a block
    block = b.create_block([tx_transfer_signed])
    b.write_block(block)
    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)
    asset_id = Transaction.get_asset_id(tx_transfer)

    assert asset_id == tx_transfer.asset['id']


def test_asset_id_mismatch(b, user_pk):
    from bigchaindb.models import Transaction
    from bigchaindb.common.exceptions import AssetIdMismatch

    tx1 = Transaction.create([b.me], [([user_pk], 1)],
                             metadata={'msg': random.random()})
    tx2 = Transaction.create([b.me], [([user_pk], 1)],
                             metadata={'msg': random.random()})

    with pytest.raises(AssetIdMismatch):
        Transaction.get_asset_id([tx1, tx2])


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_transactions_by_asset_id(b, user_pk, user_sk):
    from bigchaindb.models import Transaction

    tx_create = b.get_owned_ids(user_pk).pop()
    tx_create = b.get_transaction(tx_create.txid)
    asset_id = tx_create.id
    txs = b.get_transactions_by_asset_id(asset_id)

    assert len(txs) == 1
    assert txs[0].id == tx_create.id
    assert txs[0].id == asset_id

    # create a transfer transaction
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([user_pk], 1)],
                                       tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])
    # create the block
    block = b.create_block([tx_transfer_signed])
    b.write_block(block)
    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    txs = b.get_transactions_by_asset_id(asset_id)

    assert len(txs) == 2
    assert {tx_create.id, tx_transfer.id} == set(tx.id for tx in txs)
    assert {asset_id} == {Transaction.get_asset_id(txs)}


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_transactions_by_asset_id_with_invalid_block(b, user_pk, user_sk):
    from bigchaindb.models import Transaction

    tx_create = b.get_owned_ids(user_pk).pop()
    tx_create = b.get_transaction(tx_create.txid)
    asset_id = tx_create.id
    txs = b.get_transactions_by_asset_id(asset_id)

    assert len(txs) == 1
    assert txs[0].id == tx_create.id
    assert txs[0].id == asset_id

    # create a transfer transaction
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([user_pk], 1)],
                                       tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])
    # create the block
    block = b.create_block([tx_transfer_signed])
    b.write_block(block)
    # vote the block invalid
    vote = b.vote(block.id, b.get_last_voted_block().id, False)
    b.write_vote(vote)

    txs = b.get_transactions_by_asset_id(asset_id)

    assert len(txs) == 1


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_asset_by_id(b, user_pk, user_sk):
    from bigchaindb.models import Transaction

    tx_create = b.get_owned_ids(user_pk).pop()
    tx_create = b.get_transaction(tx_create.txid)

    # create a transfer transaction
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([user_pk], 1)],
                                       tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])
    # create the block
    block = b.create_block([tx_transfer_signed])
    b.write_block(block)
    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    asset_id = Transaction.get_asset_id([tx_create, tx_transfer])
    txs = b.get_transactions_by_asset_id(asset_id)
    assert len(txs) == 2

    asset = b.get_asset_by_id(asset_id)
    assert asset == tx_create.asset


def test_create_invalid_divisible_asset(b, user_pk, user_sk):
    from bigchaindb.models import Transaction
    from bigchaindb.common.exceptions import AmountError

    # Asset amount must be more than 0
    tx = Transaction.create([user_pk], [([user_pk], 1)])
    tx.outputs[0].amount = 0
    tx.sign([user_sk])

    with pytest.raises(AmountError):
        b.validate_transaction(tx)


def test_create_valid_divisible_asset(b, user_pk, user_sk):
    from bigchaindb.models import Transaction

    tx = Transaction.create([user_pk], [([user_pk], 2)])
    tx_signed = tx.sign([user_sk])
    assert b.is_valid_transaction(tx_signed)
