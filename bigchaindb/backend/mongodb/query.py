"""Query implementation for MongoDB"""

from time import time

from pymongo import ReturnDocument

from bigchaindb import backend
from bigchaindb.backend.mongodb.changefeed import run_changefeed
from bigchaindb.common.exceptions import CyclicBlockchainError
from bigchaindb.common.transaction import Transaction
from bigchaindb.backend.exceptions import DuplicateKeyError, OperationError
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.mongodb.connection import MongoDBConnection


register_query = module_dispatch_registrar(backend.query)


@register_query(MongoDBConnection)
def write_transaction(conn, signed_transaction):
    try:
        return conn.run(
            conn.collection('backlog')
            .insert_one(signed_transaction))
    except DuplicateKeyError:
        return


@register_query(MongoDBConnection)
def update_transaction(conn, transaction_id, doc):
    # with mongodb we need to add update operators to the doc
    doc = {'$set': doc}
    return conn.run(
        conn.collection('backlog')
        .find_one_and_update(
            {'id': transaction_id},
            doc,
            return_document=ReturnDocument.AFTER))


@register_query(MongoDBConnection)
def delete_transaction(conn, *transaction_id):
    return conn.run(
        conn.collection('backlog')
        .delete_many({'id': {'$in': transaction_id}}))


@register_query(MongoDBConnection)
def get_stale_transactions(conn, reassign_delay):
    return conn.run(
        conn.collection('backlog')
        .find({'assignment_timestamp': {'$lt': time() - reassign_delay}},
              projection={'_id': False}))


@register_query(MongoDBConnection)
def get_transaction_from_block(conn, transaction_id, block_id):
    try:
        return conn.run(
            conn.collection('bigchain')
            .aggregate([
                {'$match': {'id': block_id}},
                {'$project': {
                    'block.transactions': {
                        '$filter': {
                            'input': '$block.transactions',
                            'as': 'transaction',
                            'cond': {
                                '$eq': ['$$transaction.id', transaction_id]
                                }
                            }
                        }
                    }}])
            .next()['block']['transactions']
            .pop())
    except (StopIteration, IndexError):
        # StopIteration is raised if the block was not found
        # IndexError is returned if the block is found but no transactions
        # match
        return


@register_query(MongoDBConnection)
def get_transaction_from_backlog(conn, transaction_id):
    return conn.run(
        conn.collection('backlog')
        .find_one({'id': transaction_id},
                  projection={'_id': False,
                              'assignee': False,
                              'assignment_timestamp': False}))


@register_query(MongoDBConnection)
def get_blocks_status_from_transaction(conn, transaction_id):
    return conn.run(
        conn.collection('bigchain')
        .find({'block.transactions.id': transaction_id},
              projection=['id', 'block.voters']))


@register_query(MongoDBConnection)
def get_txids_filtered(conn, asset_id, operation=None):
    match_create = {
        'block.transactions.operation': 'CREATE',
        'block.transactions.id': asset_id
    }
    match_transfer = {
        'block.transactions.operation': 'TRANSFER',
        'block.transactions.asset.id': asset_id
    }

    if operation == Transaction.CREATE:
        match = match_create
    elif operation == Transaction.TRANSFER:
        match = match_transfer
    else:
        match = {'$or': [match_create, match_transfer]}

    pipeline = [
        {'$match': match},
        {'$unwind': '$block.transactions'},
        {'$match': match},
        {'$project': {'block.transactions.id': True}}
    ]
    cursor = conn.run(
        conn.collection('bigchain')
        .aggregate(pipeline))
    return (elem['block']['transactions']['id'] for elem in cursor)


# TODO: This doesn't seem to be used anywhere
@register_query(MongoDBConnection)
def get_asset_by_id(conn, asset_id):
    cursor = conn.run(
        conn.collection('bigchain')
        .aggregate([
            {'$match': {
                'block.transactions.id': asset_id,
                'block.transactions.operation': 'CREATE'
            }},
            {'$unwind': '$block.transactions'},
            {'$match': {
                'block.transactions.id': asset_id,
                'block.transactions.operation': 'CREATE'
            }},
            {'$project': {'block.transactions.asset': True}}
        ]))
    # we need to access some nested fields before returning so lets use a
    # generator to avoid having to read all records on the cursor at this point
    return (elem['block']['transactions'] for elem in cursor)


@register_query(MongoDBConnection)
def get_spent(conn, transaction_id, output):
    cursor = conn.run(
        conn.collection('bigchain').aggregate([
            {'$match': {
                'block.transactions.inputs': {
                    '$elemMatch': {
                        'fulfills.transaction_id': transaction_id,
                        'fulfills.output_index': output,
                    },
                },
            }},
            {'$unwind': '$block.transactions'},
            {'$match': {
                'block.transactions.inputs': {
                    '$elemMatch': {
                        'fulfills.transaction_id': transaction_id,
                        'fulfills.output_index': output,
                    },
                },
            }},
        ]))
    # we need to access some nested fields before returning so lets use a
    # generator to avoid having to read all records on the cursor at this point
    return (elem['block']['transactions'] for elem in cursor)


@register_query(MongoDBConnection)
def get_spending_transactions(conn, inputs):
    cursor = conn.run(
        conn.collection('bigchain').aggregate([
            {'$match': {
                'block.transactions.inputs.fulfills': {
                    '$in': inputs,
                },
            }},
            {'$unwind': '$block.transactions'},
            {'$match': {
                'block.transactions.inputs.fulfills': {
                    '$in': inputs,
                },
            }},
        ]))
    return ((b['id'], b['block']['transactions']) for b in cursor)


@register_query(MongoDBConnection)
def get_owned_ids(conn, owner):
    cursor = conn.run(
        conn.collection('bigchain').aggregate([
            {'$match': {'block.transactions.outputs.public_keys': owner}},
            {'$unwind': '$block.transactions'},
            {'$match': {'block.transactions.outputs.public_keys': owner}}
        ]))
    return ((b['id'], b['block']['transactions']) for b in cursor)


@register_query(MongoDBConnection)
def get_votes_by_block_id(conn, block_id):
    return conn.run(
        conn.collection('votes')
        .find({'vote.voting_for_block': block_id},
              projection={'_id': False}))


@register_query(MongoDBConnection)
def get_votes_for_blocks_by_voter(conn, block_ids, node_pubkey):
    return conn.run(
        conn.collection('votes')
        .find({'vote.voting_for_block': {'$in': block_ids},
               'node_pubkey': node_pubkey},
              projection={'_id': False}))


@register_query(MongoDBConnection)
def get_votes_by_block_id_and_voter(conn, block_id, node_pubkey):
    return conn.run(
        conn.collection('votes')
        .find({'vote.voting_for_block': block_id,
               'node_pubkey': node_pubkey},
              projection={'_id': False}))


@register_query(MongoDBConnection)
def write_block(conn, block_dict):
    return conn.run(
        conn.collection('bigchain')
        .insert_one(block_dict))


@register_query(MongoDBConnection)
def get_block(conn, block_id):
    return conn.run(
        conn.collection('bigchain')
        .find_one({'id': block_id},
                  projection={'_id': False}))


@register_query(MongoDBConnection)
def write_assets(conn, assets):
    try:
        # unordered means that all the inserts will be attempted instead of
        # stopping after the first error.
        return conn.run(
            conn.collection('assets')
            .insert_many(assets, ordered=False))
    # This can happen if we try to write the same asset multiple times.
    # One case is when we write the same transaction into multiple blocks due
    # to invalid blocks.
    # The actual mongodb exception is a BulkWriteError due to a duplicated key
    # in one of the inserts.
    except OperationError:
        return


@register_query(MongoDBConnection)
def get_assets(conn, asset_ids):
    return conn.run(
        conn.collection('assets')
        .find({'id': {'$in': asset_ids}},
              projection={'_id': False}))


@register_query(MongoDBConnection)
def count_blocks(conn):
    return conn.run(
        conn.collection('bigchain')
        .count())


@register_query(MongoDBConnection)
def count_backlog(conn):
    return conn.run(
        conn.collection('backlog')
        .count())


@register_query(MongoDBConnection)
def write_vote(conn, vote):
    conn.run(conn.collection('votes').insert_one(vote))
    vote.pop('_id')
    return vote


@register_query(MongoDBConnection)
def get_genesis_block(conn):
    return conn.run(
        conn.collection('bigchain')
        .find_one(
            {'block.transactions.0.operation': 'GENESIS'},
            {'_id': False}
        ))


@register_query(MongoDBConnection)
def get_last_voted_block_id(conn, node_pubkey):
    last_voted = conn.run(
            conn.collection('votes')
            .find({'node_pubkey': node_pubkey},
                  sort=[('vote.timestamp', -1)]))

    # pymongo seems to return a cursor even if there are no results
    # so we actually need to check the count
    if last_voted.count() == 0:
        return get_genesis_block(conn)['id']

    mapping = {v['vote']['previous_block']: v['vote']['voting_for_block']
               for v in last_voted}

    last_block_id = list(mapping.values())[0]

    explored = set()

    while True:
        try:
            if last_block_id in explored:
                raise CyclicBlockchainError()
            explored.add(last_block_id)
            last_block_id = mapping[last_block_id]
        except KeyError:
            break

    return last_block_id


@register_query(MongoDBConnection)
def get_new_blocks_feed(conn, start_block_id):
    namespace = conn.dbname + '.bigchain'
    match = {'o.id': start_block_id, 'op': 'i', 'ns': namespace}
    # Neccesary to find in descending order since tests may write same block id several times
    query = conn.query().local.oplog.rs.find(match).sort('$natural', -1).next()['ts']
    last_ts = conn.run(query)
    feed = run_changefeed(conn, 'bigchain', last_ts)
    return (evt['o'] for evt in feed if evt['op'] == 'i')


@register_query(MongoDBConnection)
def text_search(conn, search, *, language='english', case_sensitive=False,
                diacritic_sensitive=False, text_score=False, limit=0):
    cursor = conn.run(
        conn.collection('assets')
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

    return (_remove_text_score(asset) for asset in cursor)


def _remove_text_score(asset):
    asset.pop('score', None)
    return asset
