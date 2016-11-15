def test_api_endpoint_shows_basic_info(client):
    from bigchaindb import version
    res = client.get('/')
    assert res.json['software'] == 'BigchainDB'
    assert res.json['version'] == version.__version__
