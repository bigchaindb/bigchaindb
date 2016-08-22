import pytest


@pytest.fixture
def client():
    from bigchaindb.client import temp_client
    return temp_client()


@pytest.fixture
def mock_requests_post(monkeypatch):
    class MockResponse:
        def __init__(self, json):
            self._json = json

        def json(self):
            return self._json

    def mockreturn(*args, **kwargs):
        return MockResponse(kwargs.get('json'))

    monkeypatch.setattr('requests.post', mockreturn)

@pytest.fixture
def mock_bigchaindb_sign(monkeypatch):
    def mockreturn(transaction, private_key, bigchain):
        return transaction

    monkeypatch.setattr('bigchaindb.util.sign_tx', mockreturn)


def test_temp_client_returns_a_temp_client():
    from bigchaindb.client import temp_client
    client = temp_client()
    assert client.public_key
    assert client.private_key


@pytest.mark.usefixtures('restore_config')
def test_client_can_create_assets(mock_requests_post, client):
    from bigchaindb import util

    tx = client.create()

    # XXX: `CREATE` operations require the node that receives the transaction to modify the data in
    #      the transaction itself.
    #      `owner_before` will be overwritten with the public key of the node in the federation
    #      that will create the real transaction. `signature` will be overwritten with the new signature.
    #      Note that this scenario is ignored by this test.
    assert tx['transaction']['fulfillments'][0]['owners_before'][0] == client.public_key
    assert tx['transaction']['conditions'][0]['owners_after'][0] == client.public_key
    assert tx['transaction']['fulfillments'][0]['input'] is None

    assert util.validate_fulfillments(tx)


def test_client_can_transfer_assets(mock_requests_post, mock_bigchaindb_sign, client):
    tx = client.transfer(client.public_key, 123)
    assert tx['transaction']['fulfillments'][0]['owners_before'][0] == client.public_key
    assert tx['transaction']['conditions'][0]['owners_after'][0] == client.public_key
    assert tx['transaction']['fulfillments'][0]['input'] == 123


@pytest.mark.parametrize('pubkey,privkey', (
    (None, None), ('pubkey', None), (None, 'privkey'),
))
def test_init_client_with_incomplete_keypair(pubkey, privkey, monkeypatch):
    from bigchaindb import config
    from bigchaindb.client import Client
    from bigchaindb.exceptions import KeypairNotFoundException
    keypair = {'public': pubkey, 'private': privkey}
    monkeypatch.setitem(config, 'keypair', keypair)
    with pytest.raises(KeypairNotFoundException):
        Client()
