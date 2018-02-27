import pytest

pytestmark = pytest.mark.tendermint

VALIDATORS_ENDPOINT = '/api/v1/validators/'


def test_get_validators_endpoint(b, client, monkeypatch):

    def mock_get(uri):
        return MockResponse()
    monkeypatch.setattr('requests.get', mock_get)

    res = client.get(VALIDATORS_ENDPOINT)

    assert is_validator(res.json[0])
    assert res.status_code == 200


def test_get_validators_500_endpoint(b, client, monkeypatch):

    def mock_get(uri):
        return 'InvalidResponse'
    monkeypatch.setattr('requests.get', mock_get)

    res = client.get(VALIDATORS_ENDPOINT)
    assert res.status_code == 500


# Helper
def is_validator(v):
    return ('pub_key' in v) and ('voting_power' in v)


class MockResponse():

    def json(self):
        return {'id': '',
                'jsonrpc': '2.0',
                'result':
                {'block_height': 5,
                 'validators': [
                     {'accum': 0,
                      'address': 'F5426F0980E36E03044F74DD414248D29ABCBDB2',
                      'pub_key': {'data': '4E2685D9016126864733225BE00F005515200727FBAB1312FC78C8B76831255A',
                                  'type': 'ed25519'},
                      'voting_power': 10}]}}
