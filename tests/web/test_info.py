from unittest import mock


def test_api_root_url_shows_basic_info(client):
    from bigchaindb import version
    res = client.get('/')
    assert res.json['software'] == 'BigchainDB'
    assert res.json['version'] == version.__version__


def test_api_v1_endpoint(client):
    with mock.patch('bigchaindb.version.__short_version__', 'tst'):
        res = client.get('/api/v1')
    docs_url = ['https://docs.bigchaindb.com/projects/server/en/',
                'tst',
                '/drivers-clients/http-client-server-api.html',
                ]
    assert res.json == {
        '_links': {
            'docs': {'href': ''.join(docs_url)},
            'self': {'href': 'http://localhost/api/v1/'},
            'statuses': {'href': 'http://localhost/api/v1/statuses/'},
            'transactions': {'href': 'http://localhost/api/v1/transactions/'}
        }
    }
