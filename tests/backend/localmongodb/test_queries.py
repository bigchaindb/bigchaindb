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


def test_write_metadata():
    from bigchaindb.backend import connect, query
    conn = connect()

    metadata = [
        {'id': 1, 'data': '1'},
        {'id': 2, 'data': '2'},
        {'id': 3, 'data': '3'}
    ]

    # write the assets
    query.store_metadatas(conn, deepcopy(metadata))

    # check that 3 assets were written to the database
    cursor = conn.db.metadata.find({}, projection={'_id': False})\
                             .sort('id', pymongo.ASCENDING)

    assert cursor.count() == 3
    assert list(cursor) == metadata


def test_get_metadata():
    from bigchaindb.backend import connect, query
    conn = connect()

    metadata = [
        {'id': 1, 'metadata': None},
        {'id': 2, 'metadata': {'key': 'value'}},
        {'id': 3, 'metadata': '3'},
    ]

    conn.db.metadata.insert_many(deepcopy(metadata), ordered=False)

    for meta in metadata:
        assert query.get_metadata(conn, [meta['id']])


def test_text_metadata():
    from ..mongodb.test_queries import test_text_search

    test_text_search('metadata')


def test_get_owned_ids(signed_create_tx, user_pk):
    from bigchaindb.backend import connect, query
    conn = connect()

    # insert a transaction
    conn.db.transactions.insert_one(signed_create_tx.to_dict())

    txns = list(query.get_owned_ids(conn, user_pk))

    assert txns[0] == signed_create_tx.to_dict()


def test_get_spending_transactions(user_pk, user_sk):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Transaction
    conn = connect()

    out = [([user_pk], 1)]
    tx1 = Transaction.create([user_pk], out * 3)
    tx1.sign([user_sk])
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


def test_store_block():
    from bigchaindb.backend import connect, query
    from bigchaindb.tendermint.lib import Block
    conn = connect()

    block = Block(app_hash='random_utxo',
                  height=3,
                  transactions=[])
    query.store_block(conn, block._asdict())
    cursor = conn.db.blocks.find({}, projection={'_id': False})
    assert cursor.count() == 1


def test_get_block():
    from bigchaindb.backend import connect, query
    from bigchaindb.tendermint.lib import Block
    conn = connect()

    block = Block(app_hash='random_utxo',
                  height=3,
                  transactions=[])

    conn.db.blocks.insert_one(block._asdict())

    block = dict(query.get_block(conn, 3))
    assert block['height'] == 3


def test_delete_zombie_transactions(signed_create_tx, signed_transfer_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.tendermint.lib import Block
    conn = connect()

    conn.db.transactions.insert_one(signed_create_tx.to_dict())
    query.store_asset(conn, {'id': signed_create_tx.id})
    block = Block(app_hash='random_utxo',
                  height=3,
                  transactions=[signed_create_tx.id])
    query.store_block(conn, block._asdict())

    conn.db.transactions.insert_one(signed_transfer_tx.to_dict())
    query.store_metadatas(conn, [{'id': signed_transfer_tx.id}])

    query.delete_zombie_transactions(conn)
    assert query.get_transaction(conn, signed_transfer_tx.id) is None
    assert query.get_asset(conn, signed_transfer_tx.id) is None
    assert list(query.get_metadata(conn, [signed_transfer_tx.id])) == []

    assert query.get_transaction(conn, signed_create_tx.id) is not None
    assert query.get_asset(conn, signed_create_tx.id) is not None


def test_delete_latest_block(signed_create_tx, signed_transfer_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.tendermint.lib import Block
    conn = connect()

    conn.db.transactions.insert_one(signed_create_tx.to_dict())
    query.store_asset(conn, {'id': signed_create_tx.id})
    block = Block(app_hash='random_utxo',
                  height=51,
                  transactions=[signed_create_tx.id])
    query.store_block(conn, block._asdict())
    query.delete_latest_block(conn)

    assert query.get_transaction(conn, signed_create_tx.id) is None
    assert query.get_asset(conn, signed_create_tx.id) is None
    assert query.get_block(conn, 51) is None


def test_delete_zero_unspent_outputs(db_context, utxoset):
    from bigchaindb.backend import query
    unspent_outputs, utxo_collection = utxoset
    delete_res = query.delete_unspent_outputs(db_context.conn)
    assert delete_res is None
    assert utxo_collection.count() == 3
    assert utxo_collection.find(
        {'$or': [
            {'transaction_id': 'a', 'output_index': 0},
            {'transaction_id': 'b', 'output_index': 0},
            {'transaction_id': 'a', 'output_index': 1},
        ]}
    ).count() == 3


def test_delete_one_unspent_outputs(db_context, utxoset):
    from bigchaindb.backend import query
    unspent_outputs, utxo_collection = utxoset
    delete_res = query.delete_unspent_outputs(db_context.conn,
                                              unspent_outputs[0])
    assert delete_res['n'] == 1
    assert utxo_collection.find(
        {'$or': [
            {'transaction_id': 'a', 'output_index': 1},
            {'transaction_id': 'b', 'output_index': 0},
        ]}
    ).count() == 2
    assert utxo_collection.find(
            {'transaction_id': 'a', 'output_index': 0}).count() == 0


def test_delete_many_unspent_outputs(db_context, utxoset):
    from bigchaindb.backend import query
    unspent_outputs, utxo_collection = utxoset
    delete_res = query.delete_unspent_outputs(db_context.conn,
                                              *unspent_outputs[::2])
    assert delete_res['n'] == 2
    assert utxo_collection.find(
        {'$or': [
            {'transaction_id': 'a', 'output_index': 0},
            {'transaction_id': 'b', 'output_index': 0},
        ]}
    ).count() == 0
    assert utxo_collection.find(
            {'transaction_id': 'a', 'output_index': 1}).count() == 1


def test_store_zero_unspent_output(db_context, utxo_collection):
    from bigchaindb.backend import query
    res = query.store_unspent_outputs(db_context.conn)
    assert res is None
    assert utxo_collection.count() == 0


def test_store_one_unspent_output(db_context,
                                  unspent_output_1, utxo_collection):
    from bigchaindb.backend import query
    res = query.store_unspent_outputs(db_context.conn, unspent_output_1)
    assert res.acknowledged
    assert len(res.inserted_ids) == 1
    assert utxo_collection.find(
        {'transaction_id': unspent_output_1['transaction_id'],
         'output_index': unspent_output_1['output_index']}
    ).count() == 1


def test_store_many_unspent_outputs(db_context,
                                    unspent_outputs, utxo_collection):
    from bigchaindb.backend import query
    res = query.store_unspent_outputs(db_context.conn, *unspent_outputs)
    assert res.acknowledged
    assert len(res.inserted_ids) == 3
    assert utxo_collection.find(
        {'transaction_id': unspent_outputs[0]['transaction_id']}
    ).count() == 3


def test_get_unspent_outputs(db_context, utxoset):
    from bigchaindb.backend import query
    cursor = query.get_unspent_outputs(db_context.conn)
    assert cursor.count() == 3
    retrieved_utxoset = list(cursor)
    unspent_outputs, utxo_collection = utxoset
    assert retrieved_utxoset == list(
        utxo_collection.find(projection={'_id': False}))
    assert retrieved_utxoset == unspent_outputs
