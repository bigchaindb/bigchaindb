# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest
import json
import urllib.parse

QUERY_ASSETS_ENDPOINT = '/api/v1/query-assets/'

@pytest.mark.bdb
def test_query_assets_with_query(client, b, alice):
    from bigchaindb.models import Transaction
    # create two assets
    asset1 = {'msg': 'abc 1'}
    asset2 = {'msg': 'abc 2'}
    tx1 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                             asset=asset1).sign([alice.private_key])
    tx2 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                             asset=asset2).sign([alice.private_key])

    b.store_bulk_transactions([tx1])
    b.store_bulk_transactions([tx2])

    res = client.get(QUERY_ASSETS_ENDPOINT + f"?query={urllib.parse.quote(json.dumps({'data.msg': 'abc 1'}))}")
    print(res)
    assert json.loads(res.json)[0]["data"] == {'msg': 'abc 1'}
    assert res.status_code == 200

@pytest.mark.bdb
def test_query_assets_with_empty_query(client, b, alice):
    from bigchaindb.models import Transaction
    # create two assets
    asset1 = {'msg': 'abc 1'}
    asset2 = {'msg': 'abc 2'}
    tx1 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                             asset=asset1).sign([alice.private_key])
    tx2 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                             asset=asset2).sign([alice.private_key])

    b.store_bulk_transactions([tx1])
    b.store_bulk_transactions([tx2])

    res = client.get(QUERY_ASSETS_ENDPOINT + f"?query={urllib.parse.quote(json.dumps({}))}")
    print(res)
    assert json.loads(res.json)[0]["data"] == {'msg': 'abc 1'}
    assert json.loads(res.json)[1]["data"] == {'msg': 'abc 2'}
    assert res.status_code == 200


@pytest.mark.bdb
def test_query_assets_with_empty_query_limit(client, b, alice):
    from bigchaindb.models import Transaction
    # create two assets
    asset1 = {'msg': 'abc 1'}
    asset2 = {'msg': 'abc 2'}
    tx1 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                             asset=asset1).sign([alice.private_key])
    tx2 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                             asset=asset2).sign([alice.private_key])

    b.store_bulk_transactions([tx1])
    b.store_bulk_transactions([tx2])

    res = client.get(QUERY_ASSETS_ENDPOINT + '?limit=1' + f"&query={urllib.parse.quote(json.dumps({}))}")
    print(res.json)
    assert len(json.loads(res.json)) == 1
    assert json.loads(res.json)[0]["data"] == {'msg': 'abc 1'}
    assert res.status_code == 200


@pytest.mark.bdb
def test_query_assets_with_empty_query_limit_0(client, b, alice):
    from bigchaindb.models import Transaction
    # create two assets
    asset1 = {'msg': 'abc 1'}
    asset2 = {'msg': 'abc 2'}
    tx1 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                             asset=asset1).sign([alice.private_key])
    tx2 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                             asset=asset2).sign([alice.private_key])

    b.store_bulk_transactions([tx1])
    b.store_bulk_transactions([tx2])

    res = client.get(QUERY_ASSETS_ENDPOINT + '?limit=0'+ f"&query={urllib.parse.quote(json.dumps({}))}")
    print(res.json)
    assert len(json.loads(res.json)) == 2
    assert json.loads(res.json)[0]["data"] == {'msg': 'abc 1'}
    assert json.loads(res.json)[1]["data"] == {'msg': 'abc 2'}
    assert res.status_code == 200

