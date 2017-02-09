from unittest import mock


@mock.patch('bigchaindb.version.__short_version__', 'tst')
@mock.patch('bigchaindb.version.__version__', 'tsttst')
@mock.patch('bigchaindb.config', {'keyring': ['abc'], 'keypair': {'public': 'def'}})
def test_api_root_endpoint(client):
    res = client.get('/')
    assert res.json == {
        '_links': {
            'docs': 'https://docs.bigchaindb.com/projects/server/en/vtsttst/',
            'api_v1': 'http://localhost/api/v1/',
        },
        'version': 'tsttst',
        'keyring': ['abc'],
        'public_key': 'def',
        'software': 'BigchainDB',
    }


@mock.patch('bigchaindb.version.__short_version__', 'tst')
@mock.patch('bigchaindb.version.__version__', 'tsttst')
def test_api_v1_endpoint(client):
    res = client.get('/api/v1')
    docs_url = ['https://docs.bigchaindb.com/projects/server/en/vtsttst',
                '/drivers-clients/http-client-server-api.html',
                ]
    assert res.json == {
        '_links': {
            'docs': ''.join(docs_url),
            'self': 'http://localhost/api/v1/',
            'statuses': 'http://localhost/api/v1/statuses/',
            'transactions': 'http://localhost/api/v1/transactions/',
        }
    }
