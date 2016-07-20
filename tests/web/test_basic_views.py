import json

import pytest
from bigchaindb import crypto
from bigchaindb import util


TX_ENDPOINT = '/api/v1/transactions/'


@pytest.mark.usefixtures('inputs')
def test_get_transaction_endpoint(b, client, user_vk):
    input_tx = b.get_owned_ids(user_vk).pop()
    tx = b.get_transaction(input_tx['txid'])
    res = client.get(TX_ENDPOINT + input_tx['txid'])
    assert tx == res.json


@pytest.mark.usefixtures('inputs')
def test_get_transaction_returns_404_if_not_found(client):
    res = client.get(TX_ENDPOINT + '123')
    assert res.status_code == 404


def test_api_endpoint_shows_basic_info(client):
    from bigchaindb import version
    res = client.get('/')
    assert res.json['software'] == 'BigchainDB'
    assert res.json['version'] == version.__version__


def test_post_create_transaction_endpoint(b, client):
    keypair = crypto.generate_key_pair()

    tx = util.create_and_sign_tx(keypair[0], keypair[1], keypair[1], None, 'CREATE')

    res = client.post(TX_ENDPOINT, data=json.dumps(tx))
    assert res.json['transaction']['fulfillments'][0]['current_owners'][0] == b.me
    assert res.json['transaction']['conditions'][0]['new_owners'][0] == keypair[1]


@pytest.mark.usefixtures('inputs')
def test_post_transfer_transaction_endpoint(b, client, user_vk, user_sk):
    to_keypair = crypto.generate_key_pair()
    input_valid = b.get_owned_ids(user_vk).pop()

    transfer = util.create_and_sign_tx(user_sk, user_vk, to_keypair[1], input_valid)
    res = client.post(TX_ENDPOINT, data=json.dumps(transfer))

    assert res.json['transaction']['fulfillments'][0]['current_owners'][0] == user_vk
    assert res.json['transaction']['conditions'][0]['new_owners'][0] == to_keypair[1]

