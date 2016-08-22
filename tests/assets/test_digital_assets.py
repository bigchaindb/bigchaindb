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

    
