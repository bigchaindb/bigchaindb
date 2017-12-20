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
def get_transaction(conn, transaction_id):
    try:
        return conn.run(
            conn.collection('transactions')
            .find_one({'id': transaction_id}, {'_id': 0}))
    except IndexError:
        pass


@register_query(LocalMongoDBConnection)
def store_asset(conn, asset):
    try:
        return conn.run(
            conn.collection('assets')
            .insert_one(asset))
    except DuplicateKeyError:
        pass


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
