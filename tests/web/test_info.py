from unittest import mock


@mock.patch('bigchaindb.version.__short_version__', 'tst')
@mock.patch('bigchaindb.version.__version__', 'tsttst')
@mock.patch('bigchaindb.config', {'keyring': ['abc'], 'keypair': {'public': 'def'}})
def test_api_root_endpoint(client):
    res = client.get('/')
    docs_url = ['https://docs.bigchaindb.com/projects/server/en/vtsttst',
                '/http-client-server-api.html']
    assert res.json == {
        'api': {
            'v1': {
                'docs': ''.join(docs_url),
                'transactions': '/api/v1/transactions/',
                'statuses': '/api/v1/statuses/',
                'assets': '/api/v1/assets/',
                'outputs': '/api/v1/outputs/',
                'streams': 'ws://localhost:9985/api/v1/streams/valid_transactions',
            }
        },
        'docs': 'https://docs.bigchaindb.com/projects/server/en/vtsttst/',
        'version': 'tsttst',
        'keyring': ['abc'],
        'public_key': 'def',
        'software': 'BigchainDB',
    }


@mock.patch('bigchaindb.version.__short_version__', 'tst')
@mock.patch('bigchaindb.version.__version__', 'tsttst')
def test_api_v1_endpoint(client):
    docs_url = ['https://docs.bigchaindb.com/projects/server/en/vtsttst',
                '/http-client-server-api.html']
    api_v1_info = {
        'docs': ''.join(docs_url),
        'transactions': '/transactions/',
        'statuses': '/statuses/',
        'assets': '/assets/',
        'outputs': '/outputs/',
        'streams': 'ws://localhost:9985/api/v1/streams/valid_transactions',
    }
    res = client.get('/api/v1')
    assert res.json == api_v1_info
