from copy import deepcopy

import pytest
import pymongo

pytestmark = pytest.mark.tendermint


@pytest.mark.bdb
def test_get_txids_filtered(signed_create_tx, signed_transfer_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Transaction
    conn = connect()

    # create and insert two blocks, one for the create and one for the
    # transfer transaction
    conn.db.transactions.insert_one(signed_create_tx.to_dict())
    conn.db.transactions.insert_one(signed_transfer_tx.to_dict())

    asset_id = Transaction.get_asset_id([signed_create_tx, signed_transfer_tx])

    # Test get by just asset id
    txids = set(query.get_txids_filtered(conn, asset_id))
    assert txids == {signed_create_tx.id, signed_transfer_tx.id}

    # Test get by asset and CREATE
    txids = set(query.get_txids_filtered(conn, asset_id, Transaction.CREATE))
    assert txids == {signed_create_tx.id}

    # Test get by asset and TRANSFER
    txids = set(query.get_txids_filtered(conn, asset_id, Transaction.TRANSFER))
    assert txids == {signed_transfer_tx.id}


@pytest.mark.bdb
def test_write_assets():
    from bigchaindb.backend import connect, query
    conn = connect()

    assets = [
        {'id': 1, 'data': '1'},
        {'id': 2, 'data': '2'},
        {'id': 3, 'data': '3'},
        # Duplicated id. Should not be written to the database
        {'id': 1, 'data': '1'},
    ]

    # write the assets
    for asset in assets:
        query.store_asset(conn, deepcopy(asset))

    # check that 3 assets were written to the database
    cursor = conn.db.assets.find({}, projection={'_id': False})\
                           .sort('id', pymongo.ASCENDING)

    assert cursor.count() == 3
    assert list(cursor) == assets[:-1]


@pytest.mark.bdb
def test_get_assets():
    from bigchaindb.backend import connect, query
    conn = connect()

    assets = [
        {'id': 1, 'data': '1'},
        {'id': 2, 'data': '2'},
        {'id': 3, 'data': '3'},
    ]

    conn.db.assets.insert_many(deepcopy(assets), ordered=False)

    for asset in assets:
        assert query.get_asset(conn, asset['id'])


@pytest.mark.bdb
@pytest.mark.tendermint
def test_text_search():
    from ..mongodb.test_queries import test_text_search

    test_text_search()
