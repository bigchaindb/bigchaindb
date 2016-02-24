import json

import pytest
from bigchaindb import crypto
from bigchaindb import util


@pytest.mark.usefixtures('inputs')
def test_get_transaction_endpoint(b, client, user_public_key):
    input_tx = b.get_owned_ids(user_public_key).pop()
    tx = b.get_transaction(input_tx)

    res = client.get('/tx/{}'.format(input_tx))
    assert tx == res.json


def test_post_create_transaction_endpoint(b, client):
    keypair = crypto.generate_key_pair()

    tx = util.create_and_sign_tx(keypair[0], keypair[1], keypair[1], None, 'CREATE')

    res = client.post('/tx/', data=json.dumps(tx))
    assert res.json['transaction']['current_owner'] == b.me
    assert res.json['transaction']['new_owner'] == keypair[1]


def test_post_transfer_transaction_endpoint(b, client):
    from_keypair = crypto.generate_key_pair()
    to_keypair = crypto.generate_key_pair()

    tx = util.create_and_sign_tx(from_keypair[0], from_keypair[1], from_keypair[1], None, 'CREATE')
    res = client.post('/tx/', data=json.dumps(tx))
    tx_id = res.json['id']

    transfer = util.create_and_sign_tx(from_keypair[0], from_keypair[1], to_keypair[1], tx_id)
    res = client.post('/tx/', data=json.dumps(transfer))

    assert res.json['transaction']['current_owner'] == from_keypair[1]
    assert res.json['transaction']['new_owner'] == to_keypair[1]

