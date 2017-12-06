from copy import deepcopy

import pytest
import pymongo

pytestmark = [pytest.mark.tendermint, pytest.mark.localmongodb, pytest.mark.bdb]


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


def test_text_search():
    from ..mongodb.test_queries import test_text_search

    test_text_search('assets')


def test_get_owned_ids(signed_create_tx, user_pk):
    from bigchaindb.backend import connect, query
    conn = connect()

    # insert a transaction
    conn.db.transactions.insert_one(signed_create_tx.to_dict())

    txns = list(query.get_owned_ids(conn, user_pk))

    assert txns[0] == signed_create_tx.to_dict()


def test_get_spending_transactions(user_pk):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Transaction
    conn = connect()

    out = [([user_pk], 1)]
    tx1 = Transaction.create([user_pk], out * 3)
    inputs = tx1.to_inputs()
    tx2 = Transaction.transfer([inputs[0]], out, tx1.id)
    tx3 = Transaction.transfer([inputs[1]], out, tx1.id)
    tx4 = Transaction.transfer([inputs[2]], out, tx1.id)
    txns = [tx.to_dict() for tx in [tx1, tx2, tx3, tx4]]
    conn.db.transactions.insert_many(txns)

    links = [inputs[0].fulfills.to_dict(), inputs[2].fulfills.to_dict()]
    txns = list(query.get_spending_transactions(conn, links))

    # tx3 not a member because input 1 not asked for
    assert txns == [tx2.to_dict(), tx4.to_dict()]
