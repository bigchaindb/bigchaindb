# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

"""Query implementation for MongoDB"""

from pymongo import DESCENDING

from bigchaindb import backend
from bigchaindb.backend.exceptions import DuplicateKeyError
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection
from bigchaindb.common.transaction import Transaction

register_query = module_dispatch_registrar(backend.query)


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
    query = {'inputs':
             {'$elemMatch':
              {'$and': [{'fulfills.transaction_id': transaction_id},
                        {'fulfills.output_index': output}]}}}

    return conn.run(
        conn.collection('transactions')
            .find(query, {'_id': 0}))


@register_query(LocalMongoDBConnection)
def get_latest_block(conn):
    return conn.run(
        conn.collection('blocks')
        .find_one(projection={'_id': False},
                  sort=[('height', DESCENDING)]))


@register_query(LocalMongoDBConnection)
def store_block(conn, block):
    try:
        return conn.run(
            conn.collection('blocks')
            .insert_one(block))
    except DuplicateKeyError:
        pass


@register_query(LocalMongoDBConnection)
def get_txids_filtered(conn, asset_id, operation=None, last_tx=None):

    match = {
        Transaction.CREATE: {'operation': 'CREATE', 'id': asset_id},
        Transaction.TRANSFER: {'operation': 'TRANSFER', 'asset.id': asset_id},
        None: {'$or': [{'asset.id': asset_id}, {'id': asset_id}]},
    }[operation]

    cursor = conn.run(conn.collection('transactions').find(match))

    if last_tx:
        cursor = cursor.sort([('$natural', DESCENDING)]).limit(1)

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
    transaction_ids = [i['transaction_id'] for i in inputs]
    output_indexes = [i['output_index'] for i in inputs]
    query = {'inputs':
             {'$elemMatch':
              {'$and':
               [
                   {'fulfills.transaction_id': {'$in': transaction_ids}},
                   {'fulfills.output_index': {'$in': output_indexes}}
               ]}}}

    cursor = conn.run(
        conn.collection('transactions').find(query, {'_id': False}))
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
            conn.collection('utxos').delete_many({
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
    return conn.run(
        conn.collection('pre_commit')
        .replace_one({}, state, upsert=True)
    )


@register_query(LocalMongoDBConnection)
def get_pre_commit_state(conn):
    return conn.run(conn.collection('pre_commit').find_one())


@register_query(LocalMongoDBConnection)
def store_validator_set(conn, validators_update):
    height = validators_update['height']
    return conn.run(
        conn.collection('validators').replace_one(
            {'height': height},
            validators_update,
            upsert=True
        )
    )


@register_query(LocalMongoDBConnection)
def delete_validator_set(conn, height):
    return conn.run(
        conn.collection('validators').delete_many({'height': height})
    )


@register_query(LocalMongoDBConnection)
def store_election(conn, election_id, height, is_concluded):
    return conn.run(
        conn.collection('elections').replace_one(
            {'election_id': election_id,
             'height': height},
            {'election_id': election_id,
             'height': height,
             'is_concluded': is_concluded},
            upsert=True,
        )
    )


@register_query(LocalMongoDBConnection)
def store_elections(conn, elections):
    return conn.run(
        conn.collection('elections').insert_many(elections)
    )


@register_query(LocalMongoDBConnection)
def delete_elections(conn, height):
    return conn.run(
        conn.collection('elections').delete_many({'height': height})
    )


@register_query(LocalMongoDBConnection)
def get_validator_set(conn, height=None):
    query = {}
    if height is not None:
        query = {'height': {'$lte': height}}

    cursor = conn.run(
        conn.collection('validators')
        .find(query, projection={'_id': False})
        .sort([('height', DESCENDING)])
        .limit(1)
    )

    return next(cursor, None)


@register_query(LocalMongoDBConnection)
def get_election(conn, election_id):
    query = {'election_id': election_id}

    return conn.run(
        conn.collection('elections')
        .find_one(query, projection={'_id': False},
                  sort=[('height', DESCENDING)])
    )


@register_query(LocalMongoDBConnection)
def get_asset_tokens_for_public_key(conn, asset_id, public_key):
    query = {'outputs.public_keys': [public_key],
             'asset.id': asset_id}

    cursor = conn.run(
        conn.collection('transactions').aggregate([
            {'$match': query},
            {'$project': {'_id': False}}
        ]))
    return cursor


@register_query(LocalMongoDBConnection)
def store_abci_chain(conn, height, chain_id, is_synced=True):
    return conn.run(
        conn.collection('abci_chains').replace_one(
            {'height': height},
            {'height': height, 'chain_id': chain_id,
             'is_synced': is_synced},
            upsert=True,
        )
    )


@register_query(LocalMongoDBConnection)
def delete_abci_chain(conn, height):
    return conn.run(
        conn.collection('abci_chains').delete_many({'height': height})
    )


@register_query(LocalMongoDBConnection)
def get_latest_abci_chain(conn):
    return conn.run(
        conn.collection('abci_chains')
            .find_one(projection={'_id': False}, sort=[('height', DESCENDING)])
    )
