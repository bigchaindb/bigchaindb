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


@pytest.mark.parametrize('table', ['assets', 'metadata'])
def test_text_search(table):
    from bigchaindb.backend import connect, query
    conn = connect()

    # Example data and tests cases taken from the mongodb documentation
    # https://docs.mongodb.com/manual/reference/operator/query/text/
    objects = [
        {'id': 1, 'subject': 'coffee', 'author': 'xyz', 'views': 50},
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5},
        {'id': 3, 'subject': 'Baking a cake', 'author': 'abc', 'views': 90},
        {'id': 4, 'subject': 'baking', 'author': 'xyz', 'views': 100},
        {'id': 5, 'subject': 'Café Con Leche', 'author': 'abc', 'views': 200},
        {'id': 6, 'subject': 'Сырники', 'author': 'jkl', 'views': 80},
        {'id': 7, 'subject': 'coffee and cream', 'author': 'efg', 'views': 10},
        {'id': 8, 'subject': 'Cafe con Leche', 'author': 'xyz', 'views': 10}
    ]

    # insert the assets
    conn.db[table].insert_many(deepcopy(objects), ordered=False)

    # test search single word
    assert list(query.text_search(conn, 'coffee', table=table)) == [
        {'id': 1, 'subject': 'coffee', 'author': 'xyz', 'views': 50},
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5},
        {'id': 7, 'subject': 'coffee and cream', 'author': 'efg', 'views': 10},
    ]

    # match any of the search terms
    assert list(query.text_search(conn, 'bake coffee cake', table=table)) == [
        {'author': 'abc', 'id': 3, 'subject': 'Baking a cake', 'views': 90},
        {'author': 'xyz', 'id': 1, 'subject': 'coffee', 'views': 50},
        {'author': 'xyz', 'id': 4, 'subject': 'baking', 'views': 100},
        {'author': 'efg', 'id': 2, 'subject': 'Coffee Shopping', 'views': 5},
        {'author': 'efg', 'id': 7, 'subject': 'coffee and cream', 'views': 10}
    ]

    # search for a phrase
    assert list(query.text_search(conn, '\"coffee shop\"', table=table)) == [
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5},
    ]

    # exclude documents that contain a term
    assert list(query.text_search(conn, 'coffee -shop', table=table)) == [
        {'id': 1, 'subject': 'coffee', 'author': 'xyz', 'views': 50},
        {'id': 7, 'subject': 'coffee and cream', 'author': 'efg', 'views': 10},
    ]

    # search different language
    assert list(query.text_search(conn, 'leche', language='es', table=table)) == [
        {'id': 5, 'subject': 'Café Con Leche', 'author': 'abc', 'views': 200},
        {'id': 8, 'subject': 'Cafe con Leche', 'author': 'xyz', 'views': 10}
    ]

    # case and diacritic insensitive search
    assert list(query.text_search(conn, 'сы́рники CAFÉS', table=table)) == [
        {'id': 6, 'subject': 'Сырники', 'author': 'jkl', 'views': 80},
        {'id': 5, 'subject': 'Café Con Leche', 'author': 'abc', 'views': 200},
        {'id': 8, 'subject': 'Cafe con Leche', 'author': 'xyz', 'views': 10}
    ]

    # case sensitive search
    assert list(query.text_search(conn, 'Coffee', case_sensitive=True, table=table)) == [
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5},
    ]

    # diacritic sensitive search
    assert list(query.text_search(conn, 'CAFÉ', diacritic_sensitive=True, table=table)) == [
        {'id': 5, 'subject': 'Café Con Leche', 'author': 'abc', 'views': 200},
    ]

    # return text score
    assert list(query.text_search(conn, 'coffee', text_score=True, table=table)) == [
        {'id': 1, 'subject': 'coffee', 'author': 'xyz', 'views': 50, 'score': 1.0},
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5, 'score': 0.75},
        {'id': 7, 'subject': 'coffee and cream', 'author': 'efg', 'views': 10, 'score': 0.75},
    ]

    # limit search result
    assert list(query.text_search(conn, 'coffee', limit=2, table=table)) == [
        {'id': 1, 'subject': 'coffee', 'author': 'xyz', 'views': 50},
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5},
    ]


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
    from bigchaindb.lib import Block
    conn = connect()

    block = Block(app_hash='random_utxo',
                  height=3,
                  transactions=[])
    query.store_block(conn, block._asdict())
    cursor = conn.db.blocks.find({}, projection={'_id': False})
    assert cursor.count() == 1


def test_get_block():
    from bigchaindb.backend import connect, query
    from bigchaindb.lib import Block
    conn = connect()

    block = Block(app_hash='random_utxo',
                  height=3,
                  transactions=[])

    conn.db.blocks.insert_one(block._asdict())

    block = dict(query.get_block(conn, 3))
    assert block['height'] == 3


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


def test_store_pre_commit_state(db_context):
    from bigchaindb.backend import query
    from bigchaindb.lib import PreCommitState

    state = PreCommitState(commit_id='test',
                           height=3,
                           transactions=[])

    query.store_pre_commit_state(db_context.conn, state._asdict())
    cursor = db_context.conn.db.pre_commit.find({'commit_id': 'test'},
                                                projection={'_id': False})
    assert cursor.count() == 1


def test_get_pre_commit_state(db_context):
    from bigchaindb.backend import query
    from bigchaindb.lib import PreCommitState

    state = PreCommitState(commit_id='test2',
                           height=3,
                           transactions=[])

    db_context.conn.db.pre_commit.insert(state._asdict())
    resp = query.get_pre_commit_state(db_context.conn, 'test2')
    assert resp == state._asdict()


def test_validator_update():
    from bigchaindb.backend import connect, query

    conn = connect()

    def gen_validator_update(height):
        return {'data': 'somedata', 'height': height}

    for i in range(1, 100, 10):
        value = gen_validator_update(i)
        query.store_validator_set(conn, value)

    v1 = query.get_validator_set(conn, 8)
    assert v1['height'] == 1

    v41 = query.get_validator_set(conn, 50)
    assert v41['height'] == 41

    v91 = query.get_validator_set(conn)
    assert v91['height'] == 91
