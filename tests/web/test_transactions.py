import json

import pytest
from bigchaindb.common import crypto


TX_ENDPOINT = '/api/v1/transactions/'


@pytest.mark.usefixtures('inputs')
def test_get_transaction_endpoint(b, client, user_pk):
    input_tx = b.get_owned_ids(user_pk).pop()
    tx = b.get_transaction(input_tx.txid)
    res = client.get(TX_ENDPOINT + tx.id)
    assert tx.to_dict() == res.json
    assert res.status_code == 200


@pytest.mark.usefixtures('inputs')
def test_get_transaction_returns_404_if_not_found(client):
    res = client.get(TX_ENDPOINT + '123')
    assert res.status_code == 404

    res = client.get(TX_ENDPOINT + '123/')
    assert res.status_code == 404


def test_post_create_transaction_endpoint(b, client):
    from bigchaindb.models import Transaction
    user_priv, user_pub = crypto.generate_key_pair()

    tx = Transaction.create([user_pub], [([user_pub], 1)])
    tx = tx.sign([user_priv])

    res = client.post(TX_ENDPOINT, data=json.dumps(tx.to_dict()))
    assert res.json['transaction']['fulfillments'][0]['owners_before'][0] == user_pub
    assert res.json['transaction']['conditions'][0]['owners_after'][0] == user_pub


def test_post_create_transaction_with_invalid_id(b, client):
    from bigchaindb.models import Transaction
    user_priv, user_pub = crypto.generate_key_pair()

    tx = Transaction.create([user_pub], [([user_pub], 1)])
    tx = tx.sign([user_priv]).to_dict()
    tx['id'] = 'abcd' * 16

    res = client.post(TX_ENDPOINT, data=json.dumps(tx))
    assert res.status_code == 400


def test_post_create_transaction_with_invalid_signature(b, client):
    from bigchaindb.models import Transaction
    user_priv, user_pub = crypto.generate_key_pair()

    tx = Transaction.create([user_pub], [([user_pub], 1)])
    tx = tx.sign([user_priv]).to_dict()
    tx['transaction']['fulfillments'][0]['fulfillment'] = 'cf:0:0'

    res = client.post(TX_ENDPOINT, data=json.dumps(tx))
    assert res.status_code == 400


def test_post_create_transaction_with_invalid_structure(client):
    res = client.post(TX_ENDPOINT, data='{}')
    assert res.status_code == 400


@pytest.mark.usefixtures('inputs')
def test_post_transfer_transaction_endpoint(b, client, user_pk, user_sk):
    sk, pk = crypto.generate_key_pair()
    from bigchaindb.models import Transaction

    user_priv, user_pub = crypto.generate_key_pair()

    input_valid = b.get_owned_ids(user_pk).pop()
    create_tx = b.get_transaction(input_valid.txid)
    transfer_tx = Transaction.transfer(create_tx.to_inputs(),
                                       [([user_pub], 1)], create_tx.asset)
    transfer_tx = transfer_tx.sign([user_sk])

    res = client.post(TX_ENDPOINT, data=json.dumps(transfer_tx.to_dict()))

    assert res.json['transaction']['fulfillments'][0]['owners_before'][0] == user_pk
    assert res.json['transaction']['conditions'][0]['owners_after'][0] == user_pub


@pytest.mark.usefixtures('inputs')
def test_post_invalid_transfer_transaction_returns_400(b, client, user_pk, user_sk):
    from bigchaindb.models import Transaction

    user_priv, user_pub = crypto.generate_key_pair()

    input_valid = b.get_owned_ids(user_pk).pop()
    create_tx = b.get_transaction(input_valid.txid)
    transfer_tx = Transaction.transfer(create_tx.to_inputs(),
                                       [([user_pub], 1)], create_tx.asset)

    res = client.post(TX_ENDPOINT, data=json.dumps(transfer_tx.to_dict()))
    assert res.status_code == 400


@pytest.mark.usefixtures('inputs')
def test_get_transaction_status_endpoint(b, client, user_pk):
    input_tx = b.get_owned_ids(user_pk).pop()
    tx, status = b.get_transaction(input_tx.txid, include_status=True)
    res = client.get(TX_ENDPOINT + input_tx.txid + "/status")
    assert status == res.json['status']
    assert res.status_code == 200

    res = client.get(TX_ENDPOINT + input_tx.txid + "/status/")
    assert status == res.json['status']
    assert res.status_code == 200


@pytest.mark.usefixtures('inputs')
def test_get_transaction_status_returns_404_if_not_found(client):
    res = client.get(TX_ENDPOINT + '123' + "/status")
    assert res.status_code == 404

    res = client.get(TX_ENDPOINT + '123' + "/status/")
    assert res.status_code == 404
