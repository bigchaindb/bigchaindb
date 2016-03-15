import json

import pytest
from bigchaindb import crypto
from bigchaindb import util


TX_ENDPOINT = '/api/v1/transactions/'
VALIDATE_ENDPOINT = '/api/v1/transactions/validate/'


@pytest.fixture
def valid_create_transaction(user_public_key):
    return util.create_tx(
        current_owner=None,
        new_owner=user_public_key,
        tx_input=None,
        operation='CREATE',
        payload={
            'IPFS_key': 'QmfQ5QAjvg4GtA3wg3adpnDJug8ktA1BxurVqBD8rtgVjP',
            'creator': 'Johnathan Plunkett',
            'title': 'The Winds of Plast'})


@pytest.fixture
def valid_transfer_transaction(user_public_key, user_private_key):
    # Requires an tx_input param to create a *valid* transfer tx
    def make_tx(tx_input):
        return util.create_and_sign_tx(
            private_key=user_private_key,
            current_owner=user_public_key,
            new_owner=user_public_key,
            tx_input=tx_input, #Fill_me_in
            operation='TRANSFER',
            payload={
                'IPFS_key': 'QmfQ5QAjvg4GtA3wg3adpnDJug8ktA1BxurVqBD8rtgVjP',
                'creator': 'Johnathan Plunkett',
                'title': 'The Winds of Plast 2: The Plastening'})
    return make_tx

@pytest.mark.usefixtures('inputs')
def test_get_transaction_endpoint(b, client, user_public_key):
    input_tx = b.get_owned_ids(user_public_key).pop()
    tx = b.get_transaction(input_tx)
    res = client.get(TX_ENDPOINT + input_tx)
    assert tx == res.json


def test_post_create_transaction_endpoint(b, client):
    keypair = crypto.generate_key_pair()

    tx = util.create_and_sign_tx(keypair[0], keypair[1], keypair[1], None, 'CREATE')

    res = client.post(TX_ENDPOINT, data=json.dumps(tx))
    assert res.json['transaction']['current_owner'] == b.me
    assert res.json['transaction']['new_owner'] == keypair[1]


def test_post_transfer_transaction_endpoint(b, client):
    from_keypair = crypto.generate_key_pair()
    to_keypair = crypto.generate_key_pair()

    tx = util.create_and_sign_tx(from_keypair[0], from_keypair[1], from_keypair[1], None, 'CREATE')
    res = client.post(TX_ENDPOINT, data=json.dumps(tx))
    tx_id = res.json['id']

    transfer = util.create_and_sign_tx(from_keypair[0], from_keypair[1], to_keypair[1], tx_id)
    res = client.post(TX_ENDPOINT, data=json.dumps(transfer))

    assert res.json['transaction']['current_owner'] == from_keypair[1]
    assert res.json['transaction']['new_owner'] == to_keypair[1]


@pytest.mark.usefixtures('inputs')
def test_post_validate_transaction_endpoint(b, client, user_public_key,
                                            valid_create_transaction,
                                            valid_transfer_transaction):
    # Validate valid CREATE tx
    res = client.post(VALIDATE_ENDPOINT,
                      data=json.dumps(valid_create_transaction))
    assert res.json['valid'] == True
    assert res.json['error'] == ''

    # Validate invalid CREATE tx
    valid_create_transaction.update({'signature': 'junk'})
    res = client.post(VALIDATE_ENDPOINT,
                      data=json.dumps(valid_create_transaction))
    assert res.json['valid'] == False
    assert res.json['error'] == \
        "OperationError('Only federation nodes can use the operation `CREATE`',)"

    # Validate valid TRANSFER tx
    res = client.post(VALIDATE_ENDPOINT, data=json.dumps(
        valid_transfer_transaction(b.get_owned_ids(user_public_key).pop())))
    assert res.json['valid'] == True
    assert res.json['error'] == ''

    # Validate invalid TRANSFER tx
    res = client.post(VALIDATE_ENDPOINT, data=json.dumps(
        valid_transfer_transaction(None)))
    assert res.json['valid'] == False
    assert res.json['error'] == \
        "ValueError('Only `CREATE` transactions can have null inputs',)"
