import pytest
from unittest.mock import MagicMock, patch

pytestmark = [pytest.mark.bdb, pytest.mark.usefixtures('inputs')]

OUTPUTS_ENDPOINT = '/api/v1/outputs/'


def test_get_outputs_endpoint(client, user_pk):
    m = MagicMock()
    m.to_uri.side_effect = lambda s: 'a%sb' % s
    with patch('bigchaindb.core.Bigchain.get_outputs_filtered') as gof:
        gof.return_value = [m, m]
        res = client.get(OUTPUTS_ENDPOINT + '?public_key={}'.format(user_pk))
    assert res.json == ['a..b', 'a..b']
    assert res.status_code == 200
    gof.assert_called_once_with(user_pk, True)


def test_get_outputs_endpoint_unspent(client, user_pk):
    m = MagicMock()
    m.to_uri.side_effect = lambda s: 'a%sb' % s
    with patch('bigchaindb.core.Bigchain.get_outputs_filtered') as gof:
        gof.return_value = [m]
        params = '?unspent=true&public_key={}'.format(user_pk)
        res = client.get(OUTPUTS_ENDPOINT + params)
    assert res.json == ['a..b']
    assert res.status_code == 200
    gof.assert_called_once_with(user_pk, False)


def test_get_outputs_endpoint_without_public_key(client):
    res = client.get(OUTPUTS_ENDPOINT)
    assert res.status_code == 400


def test_get_outputs_endpoint_with_invalid_public_key(client):
    expected = {'message': {'public_key': 'Invalid base58 ed25519 key'}}
    res = client.get(OUTPUTS_ENDPOINT + '?public_key=abc')
    assert expected == res.json
    assert res.status_code == 400


def test_get_outputs_endpoint_with_invalid_unspent(client, user_pk):
    expected = {'message': {'unspent': 'Boolean value must be "true" or "false" (lowercase)'}}
    params = '?unspent=tru&public_key={}'.format(user_pk)
    res = client.get(OUTPUTS_ENDPOINT + params)
    assert expected == res.json
    assert res.status_code == 400


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_divisble_transactions_returns_500(b, client):
    from bigchaindb.models import Transaction
    from bigchaindb.common import crypto
    import json

    TX_ENDPOINT = '/api/v1/transactions'

    def mine(tx_list):
        block = b.create_block(tx_list)
        b.write_block(block)

        # vote the block valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

    alice_priv, alice_pub = crypto.generate_key_pair()
    bob_priv, bob_pub = crypto.generate_key_pair()
    carly_priv, carly_pub = crypto.generate_key_pair()

    create_tx = Transaction.create([alice_pub], [([alice_pub], 4)])
    create_tx.sign([alice_priv])

    res = client.post(TX_ENDPOINT, data=json.dumps(create_tx.to_dict()))
    assert res.status_code == 202

    mine([create_tx])

    transfer_tx = Transaction.transfer(create_tx.to_inputs(),
                                       [([alice_pub], 3), ([bob_pub], 1)],
                                       asset_id=create_tx.id)
    transfer_tx.sign([alice_priv])

    res = client.post(TX_ENDPOINT, data=json.dumps(transfer_tx.to_dict()))
    assert res.status_code == 202

    mine([transfer_tx])

    transfer_tx_carly = Transaction.transfer([transfer_tx.to_inputs()[1]],
                                       [([carly_pub], 1)],
                                       asset_id=create_tx.id)
    transfer_tx_carly.sign([bob_priv])

    res = client.post(TX_ENDPOINT, data=json.dumps(transfer_tx_carly.to_dict()))
    assert res.status_code == 202

    mine([transfer_tx_carly])

    asset_id = create_tx.id

    url = TX_ENDPOINT + "?asset_id=" + asset_id
    assert client.get(url).status_code == 200
    assert len(client.get(url).json) == 3

    url = OUTPUTS_ENDPOINT + '?public_key=' + alice_pub
    assert client.get(url).status_code == 200

    url = OUTPUTS_ENDPOINT + '?public_key=' + bob_pub
    assert client.get(url).status_code == 200

    url = OUTPUTS_ENDPOINT + '?public_key=' + carly_pub
    assert client.get(url).status_code == 200
