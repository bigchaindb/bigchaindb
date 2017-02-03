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
