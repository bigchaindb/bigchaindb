"""Query implementation for MongoDB"""

from pymongo import DESCENDING

from bigchaindb import backend
from bigchaindb.backend.exceptions import DuplicateKeyError
from bigchaindb.common.exceptions import MultipleValidatorOperationError
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection
from bigchaindb.common.transaction import Transaction
from bigchaindb.backend.query import VALIDATOR_UPDATE_ID

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
    return conn.run(
        conn.collection('transactions')
        .find_one({'id': transaction_id}, {'_id': 0}))


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
def get_assets(conn, asset_ids):
    return conn.run(
        conn.collection('assets')
        .find({'id': {'$in': asset_ids}},
              projection={'_id': False}))


@register_query(LocalMongoDBConnection)
def get_spent(conn, transaction_id, output):
    query = {'inputs.fulfills': {
        'transaction_id': transaction_id,
        'output_index': output}}

    return conn.run(
        conn.collection('transactions')
            .find(query, {'_id': 0}))


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
def text_search(conn, search, *, language='english', case_sensitive=False,
                diacritic_sensitive=False, text_score=False, limit=0, table='assets'):
    cursor = conn.run(
        conn.collection(table)
        .find({'$text': {
                '$search': search,
                '$language': language,
                '$caseSensitive': case_sensitive,
                '$diacriticSensitive': diacritic_sensitive}},
              {'score': {'$meta': 'textScore'}, '_id': False})
        .sort([('score', {'$meta': 'textScore'})])
        .limit(limit))

    if text_score:
        return cursor

    return (_remove_text_score(obj) for obj in cursor)


def _remove_text_score(asset):
    asset.pop('score', None)
    return asset


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
def delete_transactions(conn, txn_ids):
    conn.run(conn.collection('assets').delete_many({'id': {'$in': txn_ids}}))
    conn.run(conn.collection('metadata').delete_many({'id': {'$in': txn_ids}}))
    conn.run(conn.collection('transactions').delete_many({'id': {'$in': txn_ids}}))


@register_query(LocalMongoDBConnection)
def store_unspent_outputs(conn, *unspent_outputs):
    if unspent_outputs:
        try:
            return conn.run(
                conn.collection('utxos').insert_many(
                    unspent_outputs,
                    ordered=False,
                )
            )
        except DuplicateKeyError:
            # TODO log warning at least
            pass


@register_query(LocalMongoDBConnection)
def delete_unspent_outputs(conn, *unspent_outputs):
    if unspent_outputs:
        return conn.run(
            conn.collection('utxos').remove({
                '$or': [{
                    '$and': [
                        {'transaction_id': unspent_output['transaction_id']},
                        {'output_index': unspent_output['output_index']},
                    ],
                } for unspent_output in unspent_outputs]
            })
        )


@register_query(LocalMongoDBConnection)
def get_unspent_outputs(conn, *, query=None):
    if query is None:
        query = {}
    return conn.run(conn.collection('utxos').find(query,
                                                  projection={'_id': False}))


@register_query(LocalMongoDBConnection)
def store_pre_commit_state(conn, state):
    commit_id = state['commit_id']
    return conn.run(
        conn.collection('pre_commit')
        .update({'commit_id': commit_id}, state, upsert=True)
    )


@register_query(LocalMongoDBConnection)
def get_pre_commit_state(conn, commit_id):
    return conn.run(conn.collection('pre_commit')
                    .find_one({'commit_id': commit_id},
                              projection={'_id': False}))


@register_query(LocalMongoDBConnection)
def store_validator_update(conn, validator_update):
    try:
        return conn.run(
            conn.collection('validators')
            .insert_one(validator_update))
    except DuplicateKeyError:
        raise MultipleValidatorOperationError('Validator update already exists')


@register_query(LocalMongoDBConnection)
def get_validator_update(conn, update_id=VALIDATOR_UPDATE_ID):
    return conn.run(
        conn.collection('validators')
        .find_one({'update_id': update_id}, projection={'_id': False}))


@register_query(LocalMongoDBConnection)
def delete_validator_update(conn, update_id=VALIDATOR_UPDATE_ID):
    return conn.run(
        conn.collection('validators')
        .delete_one({'update_id': update_id})
    )
