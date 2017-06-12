from unittest import mock

import pytest


@pytest.fixture
def api_v1_info():
    docs_url = ['https://docs.bigchaindb.com/projects/server/en/vtsttst',
                '/http-client-server-api.html',
                ]
    return {
        'docs': ''.join(docs_url),
        'transactions': 'http://localhost/api/v1/transactions/',
        'statuses': 'http://localhost/api/v1/statuses/',
        'assets': 'http://localhost/api/v1/assets/',
        'outputs': 'http://localhost/api/v1/outputs/',
        'streams_v1': 'ws://localhost:9985/api/v1/streams/valid_tx',
    }


@mock.patch('bigchaindb.version.__short_version__', 'tst')
@mock.patch('bigchaindb.version.__version__', 'tsttst')
@mock.patch('bigchaindb.config', {'keyring': ['abc'], 'keypair': {'public': 'def'}})
def test_api_root_endpoint(client, api_v1_info):
    res = client.get('/')
    assert res.json == {
        'api': {
            'v1': api_v1_info
        },
        'docs': 'https://docs.bigchaindb.com/projects/server/en/vtsttst/',
        'version': 'tsttst',
        'keyring': ['abc'],
        'public_key': 'def',
        'software': 'BigchainDB',
    }


@mock.patch('bigchaindb.version.__short_version__', 'tst')
@mock.patch('bigchaindb.version.__version__', 'tsttst')
def test_api_v1_endpoint(client, api_v1_info):
    res = client.get('/api/v1')
    assert res.json == api_v1_info
