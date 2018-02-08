"""Query implementation for MongoDB"""

from pymongo import DESCENDING

from bigchaindb import backend
from bigchaindb.backend.exceptions import DuplicateKeyError
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection
from bigchaindb.common.transaction import Transaction
from bigchaindb.backend import mongodb

register_query = module_dispatch_registrar(backend.query)


@register_query(LocalMongoDBConnection)
def store_transaction(conn, signed_transaction):
    try:
        return conn.run(
            conn.collection('transactions')
            .insert_one(signed_transaction))
    except DuplicateKeyError:
        pass


@register_query(LocalMongoDBConnection)
def store_transactions(conn, signed_transactions):
    return conn.run(conn.collection('transactions')
                    .insert_many(signed_transactions))


@register_query(LocalMongoDBConnection)
def get_transaction(conn, transaction_id):
    try:
        return conn.run(
            conn.collection('transactions')
            .find_one({'id': transaction_id}, {'_id': 0}))
    except IndexError:
        pass


@register_query(LocalMongoDBConnection)
def get_transactions(conn, transaction_ids):
    try:
        return conn.run(
            conn.collection('transactions')
            .find({'id': {'$in': transaction_ids}},
                  projection={'_id': False}))
    except IndexError:
        pass


@register_query(LocalMongoDBConnection)
def store_metadatas(conn, metadata):
    return conn.run(
        conn.collection('metadata')
        .insert_many(metadata, ordered=False))


@register_query(LocalMongoDBConnection)
def get_metadata(conn, transaction_ids):
    return conn.run(
        conn.collection('metadata')
        .find({'id': {'$in': transaction_ids}},
              projection={'_id': False}))


@register_query(LocalMongoDBConnection)
def store_asset(conn, asset):
    try:
        return conn.run(
            conn.collection('assets')
            .insert_one(asset))
    except DuplicateKeyError:
        pass


@register_query(LocalMongoDBConnection)
def store_assets(conn, assets):
    return conn.run(
        conn.collection('assets')
        .insert_many(assets, ordered=False))


@register_query(LocalMongoDBConnection)
def get_asset(conn, asset_id):
    try:
        return conn.run(
            conn.collection('assets')
            .find_one({'id': asset_id}, {'_id': 0, 'id': 0}))
    except IndexError:
        pass


@register_query(LocalMongoDBConnection)
def get_spent(conn, transaction_id, output):
    try:
        return conn.run(
            conn.collection('transactions')
            .find_one({'inputs.fulfills.transaction_id': transaction_id,
                       'inputs.fulfills.output_index': output},
                      {'_id': 0}))
    except IndexError:
        pass


@register_query(LocalMongoDBConnection)
def get_latest_block(conn):
    return conn.run(
        conn.collection('blocks')
        .find_one(sort=[('height', DESCENDING)]))


@register_query(LocalMongoDBConnection)
def store_block(conn, block):
    try:
        return conn.run(
            conn.collection('blocks')
            .insert_one(block))
    except DuplicateKeyError:
        pass


@register_query(LocalMongoDBConnection)
def get_txids_filtered(conn, asset_id, operation=None):
    match_create = {
        'operation': 'CREATE',
        'id': asset_id
    }
    match_transfer = {
        'operation': 'TRANSFER',
        'asset.id': asset_id
    }

    if operation == Transaction.CREATE:
        match = match_create
    elif operation == Transaction.TRANSFER:
        match = match_transfer
    else:
        match = {'$or': [match_create, match_transfer]}

    pipeline = [
        {'$match': match}
    ]
    cursor = conn.run(
        conn.collection('transactions')
        .aggregate(pipeline))
    return (elem['id'] for elem in cursor)


@register_query(LocalMongoDBConnection)
def text_search(*args, **kwargs):
    return mongodb.query.text_search(*args, **kwargs)


@register_query(LocalMongoDBConnection)
def get_owned_ids(conn, owner):
    cursor = conn.run(
        conn.collection('transactions').aggregate([
            {'$match': {'outputs.public_keys': owner}},
            {'$project': {'_id': False}}
        ]))
    return cursor


@register_query(LocalMongoDBConnection)
def get_spending_transactions(conn, inputs):
    cursor = conn.run(
        conn.collection('transactions').aggregate([
            {'$match': {
                'inputs.fulfills': {
                    '$in': inputs,
                },
            }},
            {'$project': {'_id': False}}
        ]))
    return cursor


@register_query(LocalMongoDBConnection)
def get_block(conn, block_id):
    return conn.run(
        conn.collection('blocks')
        .find_one({'height': block_id},
                  projection={'_id': False}))


@register_query(LocalMongoDBConnection)
def get_block_with_transaction(conn, txid):
    return conn.run(
        conn.collection('blocks')
        .find({'transactions': txid},
              projection={'_id': False, 'height': True}))


@register_query(LocalMongoDBConnection)
def delete_zombie_transactions(conn):
    txns = conn.run(conn.collection('transactions').find({}))
    for txn in txns:
        txn_id = txn['id']
        block = list(get_block_with_transaction(conn, txn_id))
        if len(block) == 0:
            delete_transaction(conn, txn_id)


def delete_transaction(conn, txn_id):
    conn.run(
        conn.collection('transactions').delete_one({'id': txn_id}))
    conn.run(
        conn.collection('assets').delete_one({'id': txn_id}))
    conn.run(
        conn.collection('metadata').delete_one({'id': txn_id}))


@register_query(LocalMongoDBConnection)
def delete_latest_block(conn):
    block = get_latest_block(conn)
    txn_ids = block['transactions']
    delete_transactions(conn, txn_ids)
    conn.run(conn.collection('blocks').delete_one({'height': block['height']}))


@register_query(LocalMongoDBConnection)
def delete_transactions(conn, txn_ids):
    conn.run(conn.collection('assets').delete_many({'id': {'$in': txn_ids}}))
    conn.run(conn.collection('metadata').delete_many({'id': {'$in': txn_ids}}))
    conn.run(conn.collection('transactions').delete_many({'id': {'$in': txn_ids}}))


@register_query(LocalMongoDBConnection)
def store_unspent_outputs(conn, *unspent_outputs):
    try:
        return conn.run(
            conn.collection('utxos')
            .insert_many(unspent_outputs, ordered=False))
    except DuplicateKeyError:
        # TODO log warning at least
        pass


@register_query(LocalMongoDBConnection)
def delete_unspent_outputs(conn, *unspent_outputs):
    cursor = conn.run(
            conn.collection('utxos').remove(
                {'$or': [
                    {'$and': [
                        {'transaction_id': unspent_output['transaction_id']},
                        {'output_index': unspent_output['output_index']}
                    ]}
                    for unspent_output in unspent_outputs
                ]}
                ))
    return cursor


@register_query(LocalMongoDBConnection)
def get_unspent_outputs(conn, *, query=None):
    if query is None:
        query = {}
    return conn.run(conn.collection('utxos').find(query,
                                                  projection={'_id': False}))
