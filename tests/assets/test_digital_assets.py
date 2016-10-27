import pytest
from ..db.conftest import inputs


@pytest.mark.usefixtures('inputs')
def test_asset_transfer(b, user_vk, user_sk):
    from bigchaindb.models import Transaction

    tx_input = b.get_owned_ids(user_vk).pop()
    tx_create = b.get_transaction(tx_input.txid)

    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [user_vk],
                                       tx_create.asset)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert tx_transfer_signed.asset.data_id == tx_create.asset.data_id


def test_validate_bad_asset_creation(b, user_vk):
    from bigchaindb.models import Transaction

    # `divisible` needs to be a boolean
    tx = Transaction.create([b.me], [user_vk])
    tx.asset.divisible = 1
    tx_signed = tx.sign([b.me_private])
    with pytest.raises(TypeError):
        tx_signed.validate(b)

    # `refillable` needs to be a boolean
    tx = Transaction.create([b.me], [user_vk])
    tx.asset.refillable = 1
    tx_signed = tx.sign([b.me_private])
    with pytest.raises(TypeError):
        b.validate_transaction(tx_signed)

    # `updatable` needs to be a boolean
    tx = Transaction.create([b.me], [user_vk])
    tx.asset.updatable = 1
    tx_signed = tx.sign([b.me_private])
    with pytest.raises(TypeError):
        b.validate_transaction(tx_signed)

    # `data` needs to be a dictionary
    tx = Transaction.create([b.me], [user_vk])
    tx.asset.data = 'a'
    tx_signed = tx.sign([b.me_private])
    with pytest.raises(TypeError):
        b.validate_transaction(tx_signed)

    # TODO: Check where to test for the amount
    """
    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx['transaction']['conditions'][0]['amount'] = 'a'
    tx['id'] = get_hash_data(tx['transaction'])
    tx_signed = b.sign_transaction(tx, b.me_private)
    with pytest.raises(TypeError):
        b.validate_transaction(tx_signed)

    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx['transaction']['conditions'][0]['amount'] = 2
    tx['transaction']['asset'].update({'divisible': False})
    tx['id'] = get_hash_data(tx['transaction'])
    tx_signed = b.sign_transaction(tx, b.me_private)
    with pytest.raises(AmountError):
        b.validate_transaction(tx_signed)

    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx['transaction']['conditions'][0]['amount'] = 0
    tx['id'] = get_hash_data(tx['transaction'])
    tx_signed = b.sign_transaction(tx, b.me_private)
    with pytest.raises(AmountError):
        b.validate_transaction(tx_signed)
    """


@pytest.mark.usefixtures('inputs')
def test_validate_transfer_asset_id_mismatch(b, user_vk, user_sk):
    from bigchaindb.common.exceptions import AssetIdMismatch
    from bigchaindb.models import Transaction

    tx_create = b.get_owned_ids(user_vk).pop()
    tx_create = b.get_transaction(tx_create.txid)
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [user_vk],
                                       tx_create.asset)
    tx_transfer.asset.data_id = 'aaa'
    tx_transfer_signed = tx_transfer.sign([user_sk])
    with pytest.raises(AssetIdMismatch):
        tx_transfer_signed.validate(b)


def test_get_asset_id_create_transaction(b, user_vk):
    from bigchaindb.models import Transaction, Asset

    tx_create = Transaction.create([b.me], [user_vk])
    asset_id = Asset.get_asset_id(tx_create)

    assert asset_id == tx_create.asset.data_id


@pytest.mark.usefixtures('inputs')
def test_get_asset_id_transfer_transaction(b, user_vk, user_sk):
    from bigchaindb.models import Transaction, Asset

    tx_create = b.get_owned_ids(user_vk).pop()
    tx_create = b.get_transaction(tx_create.txid)
    # create a transfer transaction
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [user_vk],
                                       tx_create.asset)
    tx_transfer_signed = tx_transfer.sign([user_sk])
    # create a block
    block = b.create_block([tx_transfer_signed])
    b.write_block(block, durability='hard')
    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)
    asset_id = Asset.get_asset_id(tx_transfer)

    assert asset_id == tx_transfer.asset.data_id


def test_asset_id_mismatch(b, user_vk):
    from bigchaindb.models import Transaction, Asset
    from bigchaindb.common.exceptions import AssetIdMismatch

    tx1 = Transaction.create([b.me], [user_vk])
    tx2 = Transaction.create([b.me], [user_vk])

    with pytest.raises(AssetIdMismatch):
        Asset.get_asset_id([tx1, tx2])


@pytest.mark.usefixtures('inputs')
def test_get_txs_by_asset_id(b, user_vk, user_sk):
    from bigchaindb.models import Transaction

    tx_create = b.get_owned_ids(user_vk).pop()
    tx_create = b.get_transaction(tx_create.txid)
    asset_id = tx_create.asset.data_id
    txs = b.get_txs_by_asset_id(asset_id)

    assert len(txs) == 1
    assert txs[0].id == tx_create.id
    assert txs[0].asset.data_id == asset_id

    # create a transfer transaction
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [user_vk],
                                       tx_create.asset)
    tx_transfer_signed = tx_transfer.sign([user_sk])
    # create the block
    block = b.create_block([tx_transfer_signed])
    b.write_block(block, durability='hard')
    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    txs = b.get_txs_by_asset_id(asset_id)

    assert len(txs) == 2
    assert tx_create.id in [t.id for t in txs]
    assert tx_transfer.id in [t.id for t in txs]
    assert asset_id == txs[0].asset.data_id
    assert asset_id == txs[1].asset.data_id
