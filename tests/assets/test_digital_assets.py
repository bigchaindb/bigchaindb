import pytest
from ..db.conftest import inputs


def test_asset_creation(b, user_vk):
    data = {'msg': 'hello'}
    tx = b.create_transaction(b.me, user_vk, None, 'CREATE', data=data)
    tx_signed = b.sign_transaction(tx, b.me_private)

    assert b.validate_transaction(tx_signed) == tx_signed
    assert tx_signed['transaction']['asset']['data'] == data
    assert tx_signed['transaction']['asset']['refillable'] is False
    assert tx_signed['transaction']['asset']['divisible'] is False
    assert tx_signed['transaction']['asset']['updatable'] is False
    assert tx_signed['transaction']['conditions'][0]['amount'] == 1


@pytest.mark.usefixtures('inputs')
def test_asset_transfer(b, user_vk, user_sk):
    tx_input = b.get_owned_ids(user_vk).pop()
    tx_create = b.get_transaction(tx_input['txid'])
    tx_transfer = b.create_transaction(user_vk, user_vk, tx_input, 'TRANSFER')
    tx_transfer_signed = b.sign_transaction(tx_transfer, user_sk)

    assert b.validate_transaction(tx_transfer_signed) == tx_transfer_signed
    assert tx_transfer_signed['transaction']['asset'] == tx_create['transaction']['asset']['id']


def test_validate_asset_arguments(b):
    from bigchaindb.exceptions import AmountError

    with pytest.raises(TypeError):
        b.create_transaction(b.me, b.me, None, 'CREATE', divisible=1)
    with pytest.raises(TypeError):
        b.create_transaction(b.me, b.me, None, 'CREATE', refillable=1)
    with pytest.raises(TypeError):
        b.create_transaction(b.me, b.me, None, 'CREATE', updatable=1)
    with pytest.raises(TypeError):
        b.create_transaction(b.me, b.me, None, 'CREATE', amount='a')
    with pytest.raises(AmountError):
        b.create_transaction(b.me, b.me, None, 'CREATE', divisible=False, amount=2)
    with pytest.raises(AmountError):
        b.create_transaction(b.me, b.me, None, 'CREATE', amount=0)


@pytest.mark.usefixtures('inputs')
def test_get_asset_id_create_transaction(b, user_vk):
    from bigchaindb.assets import get_asset_id

    tx_input = b.get_owned_ids(user_vk).pop()
    tx_create = b.get_transaction(tx_input['txid'])
    asset_id = get_asset_id(tx_input['txid'], bigchain=b)

    assert asset_id == tx_create['transaction']['asset']['id']


@pytest.mark.usefixtures('inputs')
def test_get_asset_id_transfer_transaction(b, user_vk, user_sk):
    from bigchaindb.assets import get_asset_id

    tx_input = b.get_owned_ids(user_vk).pop()
    # create a transfer transaction
    tx_transfer = b.create_transaction(user_vk, user_vk, tx_input, 'TRANSFER')
    tx_transfer_signed = b.sign_transaction(tx_transfer, user_sk)
    # create a block
    block = b.create_block([tx_transfer_signed])
    b.write_block(block, durability='hard')
    # vote the block valid
    vote = b.vote(block['id'], b.get_last_voted_block()['id'], True)
    b.write_vote(vote)
    asset_id = get_asset_id(tx_transfer['id'], bigchain=b)

    assert asset_id == tx_transfer['transaction']['asset']


@pytest.mark.usefixtures('inputs')
def test_asset_id_mismatch(b, user_vk):
    from bigchaindb.assets import get_asset_id
    from bigchaindb.exceptions import AssetIdMismatch

    tx_input1, tx_input2 = b.get_owned_ids(user_vk)[:2]

    with pytest.raises(AssetIdMismatch):
        get_asset_id([tx_input1['txid'], tx_input2['txid']], bigchain=b)
