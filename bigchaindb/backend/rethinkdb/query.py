from itertools import chain
from time import time

import rethinkdb as r

from bigchaindb import backend, utils
from bigchaindb.common import exceptions
from bigchaindb.common.transaction import Transaction
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.rethinkdb.connection import RethinkDBConnection


READ_MODE = 'majority'
WRITE_DURABILITY = 'hard'

register_query = module_dispatch_registrar(backend.query)


@register_query(RethinkDBConnection)
def write_transaction(connection, signed_transaction):
    return connection.run(
            r.table('backlog')
            .insert(signed_transaction, durability=WRITE_DURABILITY))


@register_query(RethinkDBConnection)
def update_transaction(connection, transaction_id, doc):
    return connection.run(
            r.table('backlog')
            .get(transaction_id)
            .update(doc))


@register_query(RethinkDBConnection)
def delete_transaction(connection, *transaction_id):
    return connection.run(
            r.table('backlog')
            .get_all(*transaction_id)
            .delete(durability=WRITE_DURABILITY))


@register_query(RethinkDBConnection)
def get_stale_transactions(connection, reassign_delay):
    return connection.run(
            r.table('backlog')
            .filter(lambda tx: time() - tx['assignment_timestamp'] > reassign_delay))


@register_query(RethinkDBConnection)
def get_transaction_from_block(connection, transaction_id, block_id):
    return connection.run(
            r.table('bigchain', read_mode=READ_MODE)
            .get(block_id)
            .get_field('block')
            .get_field('transactions')
            .filter(lambda tx: tx['id'] == transaction_id))[0]


@register_query(RethinkDBConnection)
def get_transaction_from_backlog(connection, transaction_id):
    return connection.run(
            r.table('backlog')
            .get(transaction_id)
            .without('assignee', 'assignment_timestamp')
            .default(None))


@register_query(RethinkDBConnection)
def get_blocks_status_from_transaction(connection, transaction_id):
    return connection.run(
            r.table('bigchain', read_mode=READ_MODE)
            .get_all(transaction_id, index='transaction_id')
            .pluck('votes', 'id', {'block': ['voters']}))


@register_query(RethinkDBConnection)
def get_txids_filtered(connection, asset_id, operation=None):
    # here we only want to return the transaction ids since later on when
    # we are going to retrieve the transaction with status validation

    parts = []

    if operation in (Transaction.CREATE, None):
        # First find the asset's CREATE transaction
        parts.append(connection.run(
            _get_asset_create_tx_query(asset_id).get_field('id')))

    if operation in (Transaction.TRANSFER, None):
        # Then find any TRANSFER transactions related to the asset
        parts.append(connection.run(
            r.table('bigchain')
            .get_all(asset_id, index='asset_id')
            .concat_map(lambda block: block['block']['transactions'])
            .filter(lambda transaction: transaction['asset']['id'] == asset_id)
            .get_field('id')))

    return chain(*parts)


@register_query(RethinkDBConnection)
def get_asset_by_id(connection, asset_id):
    return connection.run(_get_asset_create_tx_query(asset_id).pluck('asset'))


def _get_asset_create_tx_query(asset_id):
    return r.table('bigchain', read_mode=READ_MODE) \
            .get_all(asset_id, index='transaction_id') \
            .concat_map(lambda block: block['block']['transactions']) \
            .filter(lambda transaction: transaction['id'] == asset_id)


@register_query(RethinkDBConnection)
def get_spent(connection, transaction_id, output):
    return connection.run(
            r.table('bigchain', read_mode=READ_MODE)
             .get_all([transaction_id, output], index='inputs')
             .concat_map(lambda doc: doc['block']['transactions'])
             .filter(lambda transaction: transaction['inputs'].contains(
                lambda input_: input_['fulfills'] == {'txid': transaction_id, 'output': output})))


@register_query(RethinkDBConnection)
def get_owned_ids(connection, owner):
    return connection.run(
            r.table('bigchain', read_mode=READ_MODE)
             .get_all(owner, index='outputs')
             .distinct()
             .concat_map(lambda doc: doc['block']['transactions'])
             .filter(lambda tx: tx['outputs'].contains(
                lambda c: c['public_keys'].contains(owner))))


@register_query(RethinkDBConnection)
def get_votes_by_block_id(connection, block_id):
    return connection.run(
            r.table('votes', read_mode=READ_MODE)
            .between([block_id, r.minval], [block_id, r.maxval], index='block_and_voter')
            .without('id'))


@register_query(RethinkDBConnection)
def get_votes_by_block_id_and_voter(connection, block_id, node_pubkey):
    return connection.run(
            r.table('votes')
            .get_all([block_id, node_pubkey], index='block_and_voter')
            .without('id'))


@register_query(RethinkDBConnection)
def write_block(connection, block):
    return connection.run(
            r.table('bigchain')
            .insert(r.json(block.to_str()), durability=WRITE_DURABILITY))


@register_query(RethinkDBConnection)
def get_block(connection, block_id):
    return connection.run(r.table('bigchain').get(block_id))


@register_query(RethinkDBConnection)
def has_transaction(connection, transaction_id):
    return bool(connection.run(
            r.table('bigchain', read_mode=READ_MODE)
            .get_all(transaction_id, index='transaction_id').count()))


@register_query(RethinkDBConnection)
def count_blocks(connection):
    return connection.run(
            r.table('bigchain', read_mode=READ_MODE)
            .count())


@register_query(RethinkDBConnection)
def count_backlog(connection):
    return connection.run(
            r.table('backlog', read_mode=READ_MODE)
            .count())


@register_query(RethinkDBConnection)
def write_vote(connection, vote):
    return connection.run(
            r.table('votes')
            .insert(vote))


@register_query(RethinkDBConnection)
def get_genesis_block(connection):
    return connection.run(
        r.table('bigchain', read_mode=READ_MODE)
        .filter(utils.is_genesis_block)
        .nth(0))


@register_query(RethinkDBConnection)
def get_last_voted_block(connection, node_pubkey):
    try:
        # get the latest value for the vote timestamp (over all votes)
        max_timestamp = connection.run(
            r.table('votes', read_mode=READ_MODE)
            .filter(r.row['node_pubkey'] == node_pubkey)
            .max(r.row['vote']['timestamp']))['vote']['timestamp']

        last_voted = list(connection.run(
            r.table('votes', read_mode=READ_MODE)
            .filter(r.row['vote']['timestamp'] == max_timestamp)
            .filter(r.row['node_pubkey'] == node_pubkey)))

    except r.ReqlNonExistenceError:
        # return last vote if last vote exists else return Genesis block
        return get_genesis_block(connection)

    # Now the fun starts. Since the resolution of timestamp is a second,
    # we might have more than one vote per timestamp. If this is the case
    # then we need to rebuild the chain for the blocks that have been retrieved
    # to get the last one.

    # Given a block_id, mapping returns the id of the block pointing at it.
    mapping = {v['vote']['previous_block']: v['vote']['voting_for_block']
               for v in last_voted}

    # Since we follow the chain backwards, we can start from a random
    # point of the chain and "move up" from it.
    last_block_id = list(mapping.values())[0]

    # We must be sure to break the infinite loop. This happens when:
    # - the block we are currenty iterating is the one we are looking for.
    #   This will trigger a KeyError, breaking the loop
    # - we are visiting again a node we already explored, hence there is
    #   a loop. This might happen if a vote points both `previous_block`
    #   and `voting_for_block` to the same `block_id`
    explored = set()

    while True:
        try:
            if last_block_id in explored:
                raise exceptions.CyclicBlockchainError()
            explored.add(last_block_id)
            last_block_id = mapping[last_block_id]
        except KeyError:
            break

    return connection.run(
            r.table('bigchain', read_mode=READ_MODE)
            .get(last_block_id))


@register_query(RethinkDBConnection)
def get_unvoted_blocks(connection, node_pubkey):
    unvoted = connection.run(
            r.table('bigchain', read_mode=READ_MODE)
            .filter(lambda block: r.table('votes', read_mode=READ_MODE)
                                   .get_all([block['id'], node_pubkey], index='block_and_voter')
                                   .is_empty())
            .order_by(r.asc(r.row['block']['timestamp'])))

    # FIXME: I (@vrde) don't like this solution. Filtering should be done at a
    #        database level. Solving issue #444 can help untangling the situation
    unvoted_blocks = filter(lambda block: not utils.is_genesis_block(block), unvoted)
    return unvoted_blocks
