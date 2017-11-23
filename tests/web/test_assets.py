import pytest

ASSETS_ENDPOINT = '/api/v1/assets/'


@pytest.mark.tendermint
def test_get_assets_with_empty_text_search(client):
    res = client.get(ASSETS_ENDPOINT + '?search=')
    assert res.json == {'status': 400,
                        'message': 'text_search cannot be empty'}
    assert res.status_code == 400


@pytest.mark.tendermint
def test_get_assets_with_missing_text_search(client):
    res = client.get(ASSETS_ENDPOINT)
    assert res.status_code == 400


@pytest.mark.genesis
def test_get_assets(client, b):
    from bigchaindb.models import Transaction
    from bigchaindb.backend.mongodb.connection import MongoDBConnection

    if isinstance(b.connection, MongoDBConnection):
        # test returns empty list when no assets are found
        res = client.get(ASSETS_ENDPOINT + '?search=abc')
        assert res.json == []
        assert res.status_code == 200

        # create asset
        asset = {'msg': 'abc'}
        tx = Transaction.create([b.me], [([b.me], 1)],
                                asset=asset).sign([b.me_private])
        # create block
        block = b.create_block([tx])
        b.write_block(block)
        # vote valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        # test that asset is returned
        res = client.get(ASSETS_ENDPOINT + '?search=abc')
        assert res.status_code == 200
        assert len(res.json) == 1
        assert res.json[0] == {
            'data': {'msg': 'abc'},
            'id': tx.id
        }
    else:
        # test that the correct error is returned if not running MongoDB
        res = client.get(ASSETS_ENDPOINT + '?search=abc')
        assert res.status_code == 400
        assert res.json['message'].startswith('(OperationError)')


@pytest.mark.genesis
def test_get_assets_limit(client, b):
    from bigchaindb.models import Transaction
    from bigchaindb.backend.mongodb.connection import MongoDBConnection

    if isinstance(b.connection, MongoDBConnection):
        # create two assets
        asset1 = {'msg': 'abc 1'}
        asset2 = {'msg': 'abc 2'}
        tx1 = Transaction.create([b.me], [([b.me], 1)],
                                 asset=asset1).sign([b.me_private])
        tx2 = Transaction.create([b.me], [([b.me], 1)],
                                 asset=asset2).sign([b.me_private])
        # create block
        block = b.create_block([tx1, tx2])
        b.write_block(block)
        # vote valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        # test that both assets are returned without limit
        res = client.get(ASSETS_ENDPOINT + '?search=abc')
        assert res.status_code == 200
        assert len(res.json) == 2

        # test that only one asset is returned when using limit=1
        res = client.get(ASSETS_ENDPOINT + '?search=abc&limit=1')
        assert res.status_code == 200
        assert len(res.json) == 1


@pytest.mark.bdb
@pytest.mark.tendermint
def test_get_assets_tmint(client, tb):
    from bigchaindb.models import Transaction
    from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection

    if isinstance(tb.connection, LocalMongoDBConnection):
        # test returns empty list when no assets are found
        res = client.get(ASSETS_ENDPOINT + '?search=abc')
        assert res.json == []
        assert res.status_code == 200

        # create asset
        asset = {'msg': 'abc'}
        tx = Transaction.create([tb.me], [([tb.me], 1)],
                                asset=asset).sign([tb.me_private])

        tb.store_transaction(tx)

        # test that asset is returned
        res = client.get(ASSETS_ENDPOINT + '?search=abc')
        assert res.status_code == 200
        assert len(res.json) == 1
        assert res.json[0] == {
            'data': {'msg': 'abc'},
            'id': tx.id
        }


@pytest.mark.bdb
@pytest.mark.tendermint
def test_get_assets_limit_tmint(client, tb):
    from bigchaindb.models import Transaction
    from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection

    b = tb
    if isinstance(b.connection, LocalMongoDBConnection):
        # create two assets
        asset1 = {'msg': 'abc 1'}
        asset2 = {'msg': 'abc 2'}
        tx1 = Transaction.create([b.me], [([b.me], 1)],
                                 asset=asset1).sign([b.me_private])
        tx2 = Transaction.create([b.me], [([b.me], 1)],
                                 asset=asset2).sign([b.me_private])

        b.store_transaction(tx1)
        b.store_transaction(tx2)

        # test that both assets are returned without limit
        res = client.get(ASSETS_ENDPOINT + '?search=abc')
        assert res.status_code == 200
        assert len(res.json) == 2

        # test that only one asset is returned when using limit=1
        res = client.get(ASSETS_ENDPOINT + '?search=abc&limit=1')
        assert res.status_code == 200
        assert len(res.json) == 1
