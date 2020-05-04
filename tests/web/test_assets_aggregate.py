# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest
import json
import urllib.parse

AGGREGATE_ASSETS_ENDPOINT = '/api/v1/aggregate-assets/'


def insert_aggregation_assets(b, alice):
    from bigchaindb.models import Transaction
    asset1 = {'msg': 'BigchainDB 1', 'complex_key': {'complex_sub_key': 'value_1', 'aggregation_key': 'ak_1'}}
    asset2 = {'msg': 'BigchainDB 2', 'complex_key': {'complex_sub_key': 'value_2', 'aggregation_key': 'ak_1'}}
    asset3 = {'msg': 'BigchainDB 3', 'complex_key': {'complex_sub_key': 'value_3', 'aggregation_key': 'ak_2'}}
    asset4 = {'msg': 'BigchainDB 3', 'complex_key': {'complex_sub_key': 'value_4', 'aggregation_key': 'ak_3'}}
    asset5 = {'msg': 'BigchainDB 3', 'complex_key': {'complex_sub_key': 'value_5', 'aggregation_key': 'ak_3'}}
    asset6 = {'msg': 'BigchainDB 3', 'complex_key': {'complex_sub_key': 'value_6', 'aggregation_key': 'ak_3'}}

    # create the transactions
    tx1 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                                asset=asset1).sign([alice.private_key])
    tx2 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                                asset=asset2).sign([alice.private_key])
    tx3 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                                asset=asset3).sign([alice.private_key])
    tx4 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                                asset=asset4).sign([alice.private_key])
    tx5 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                                asset=asset5).sign([alice.private_key])
    tx6 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                                asset=asset6).sign([alice.private_key])

    # write the transactions to the DB
    b.store_bulk_transactions([tx1, tx2, tx3, tx4, tx5, tx6])


@pytest.mark.bdb
def test_aggregate_assets_with_query(client, b, alice):
    insert_aggregation_assets(b, alice)
    aggregation_functions = {'function_list': [{'$group': {'_id': "$data.complex_key.aggregation_key", 'count': {'$sum': 1}}}]}
    res = client.get(AGGREGATE_ASSETS_ENDPOINT + f"?aggregation_functions={urllib.parse.quote(json.dumps(aggregation_functions))}")
    assert res.json == json.dumps({"results": [{'_id': 'ak_3', 'count': 3},
                                               {'_id': 'ak_2', 'count': 1},
                                               {'_id': 'ak_1', 'count': 2}]})
    assert res.status_code == 200

@pytest.mark.bdb
def test_aggregate_assets_with_invalid_query(client, b, alice):
    insert_aggregation_assets(b, alice)
    aggregation_functions = {'something': [{'$group': {'_id': "$data.complex_key.aggregation_key", 'count': {'$sum': 1}}}]}
    res = client.get(AGGREGATE_ASSETS_ENDPOINT + f"?aggregation_functions={urllib.parse.quote(json.dumps(aggregation_functions))}")
    assert res.status_code == 400