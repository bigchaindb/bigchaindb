# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from unittest import mock


@mock.patch('bigchaindb.version.__short_version__', 'tst')
@mock.patch('bigchaindb.version.__version__', 'tsttst')
def test_api_root_endpoint(client, wsserver_base_url):
    res = client.get('/')
    docs_url = ['https://docs.bigchaindb.com/projects/server/en/vtsttst',
                '/http-client-server-api.html']
    assert res.json == {
        'api': {
            'v1': {
                'docs': ''.join(docs_url),
                'transactions': '/api/v1/transactions/',
                'blocks': '/api/v1/blocks/',
                'assets': '/api/v1/assets/',
                'outputs': '/api/v1/outputs/',
                'streams': '{}/api/v1/streams/valid_transactions'.format(
                    wsserver_base_url),
                'metadata': '/api/v1/metadata/',
                'validators': '/api/v1/validators',
            }
        },
        'docs': 'https://docs.bigchaindb.com/projects/server/en/vtsttst/',
        'version': 'tsttst',
        'software': 'BigchainDB',
    }


@mock.patch('bigchaindb.version.__short_version__', 'tst')
@mock.patch('bigchaindb.version.__version__', 'tsttst')
def test_api_v1_endpoint(client, wsserver_base_url):
    docs_url = ['https://docs.bigchaindb.com/projects/server/en/vtsttst',
                '/http-client-server-api.html']
    api_v1_info = {
        'docs': ''.join(docs_url),
        'transactions': '/transactions/',
        'blocks': '/blocks/',
        'assets': '/assets/',
        'outputs': '/outputs/',
                'streams': '{}/api/v1/streams/valid_transactions'.format(
                    wsserver_base_url),
        'metadata': '/metadata/',
        'validators': '/validators'
    }
    res = client.get('/api/v1')
    assert res.json == api_v1_info
