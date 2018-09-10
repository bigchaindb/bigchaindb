# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest

METADATA_ENDPOINT = '/api/v1/metadata/'


def test_get_metadata_with_empty_text_search(client):
    res = client.get(METADATA_ENDPOINT + '?search=')
    assert res.json == {'status': 400,
                        'message': 'text_search cannot be empty'}
    assert res.status_code == 400


def test_get_metadata_with_missing_text_search(client):
    res = client.get(METADATA_ENDPOINT)
    assert res.status_code == 400


@pytest.mark.bdb
def test_get_metadata_tendermint(client, b, alice):
    from bigchaindb.models import Transaction

    # test returns empty list when no assets are found
    res = client.get(METADATA_ENDPOINT + '?search=abc')
    assert res.json == []
    assert res.status_code == 200

    # create asset
    asset = {'msg': 'abc'}
    metadata = {'key': 'my_meta'}
    tx = Transaction.create([alice.public_key], [([alice.public_key], 1)], metadata=metadata,
                            asset=asset).sign([alice.private_key])

    b.store_bulk_transactions([tx])

    # test that metadata is returned
    res = client.get(METADATA_ENDPOINT + '?search=my_meta')
    assert res.status_code == 200
    assert len(res.json) == 1
    assert res.json[0] == {
        'metadata': {'key': 'my_meta'},
        'id': tx.id
    }


@pytest.mark.bdb
def test_get_metadata_limit_tendermint(client, b, alice):
    from bigchaindb.models import Transaction

    # create two assets
    asset1 = {'msg': 'abc 1'}
    meta1 = {'key': 'meta 1'}
    tx1 = Transaction.create([alice.public_key], [([alice.public_key], 1)], metadata=meta1,
                             asset=asset1).sign([alice.private_key])
    b.store_bulk_transactions([tx1])

    asset2 = {'msg': 'abc 2'}
    meta2 = {'key': 'meta 2'}
    tx2 = Transaction.create([alice.public_key], [([alice.public_key], 1)], metadata=meta2,
                             asset=asset2).sign([alice.private_key])
    b.store_bulk_transactions([tx2])

    # test that both assets are returned without limit
    res = client.get(METADATA_ENDPOINT + '?search=meta')
    assert res.status_code == 200
    assert len(res.json) == 2

    # test that only one asset is returned when using limit=1
    res = client.get(METADATA_ENDPOINT + '?search=meta&limit=1')
    assert res.status_code == 200
    assert len(res.json) == 1
