import logging

import rethinkdb as r

from bigchaindb import backend
from bigchaindb.common import exceptions
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.rethinkdb.connection import RethinkDBConnection


logger = logging.getLogger(__name__)
register_schema = module_dispatch_registrar(backend.schema)


@register_schema(RethinkDBConnection)
def create_database(connection, dbname):
    if connection.run(r.db_list().contains(dbname)):
        raise exceptions.DatabaseAlreadyExists('Database `{}` already exists'.format(dbname))

    logger.info('Create database `%s`.', dbname)
    connection.run(r.db_create(dbname))


@register_schema(RethinkDBConnection)
def create_tables(connection, dbname):
    for table_name in ['bigchain', 'backlog', 'votes', 'assets']:
        logger.info('Create `%s` table.', table_name)
        connection.run(r.db(dbname).table_create(table_name))


@register_schema(RethinkDBConnection)
def create_indexes(connection, dbname):
    create_bigchain_secondary_index(connection, dbname)
    create_backlog_secondary_index(connection, dbname)
    create_votes_secondary_index(connection, dbname)


@register_schema(RethinkDBConnection)
def drop_database(connection, dbname):
    try:
        logger.info('Drop database `%s`', dbname)
        connection.run(r.db_drop(dbname))
        logger.info('Done.')
    except r.ReqlOpFailedError:
        raise exceptions.DatabaseDoesNotExist('Database `{}` does not exist'.format(dbname))


def create_bigchain_secondary_index(connection, dbname):
    logger.info('Create `bigchain` secondary index.')

    # to order blocks by timestamp
    connection.run(
        r.db(dbname)
        .table('bigchain')
        .index_create('block_timestamp', r.row['block']['timestamp']))

    # to query the bigchain for a transaction id
    connection.run(
        r.db(dbname)
        .table('bigchain')
        .index_create('transaction_id', r.row['block']['transactions']['id'], multi=True))

    # secondary index for asset links (in TRANSFER transactions)
    connection.run(
        r.db(dbname)
        .table('bigchain')
        .index_create('asset_id', r.row['block']['transactions']['asset']['id'], multi=True))

    # secondary index on the public keys of outputs
    # the last reduce operation is to return a flatten list of public_keys
    # without it we would need to match exactly the public_keys list.
    # For instance querying for `pk1` would not match documents with
    # `public_keys: [pk1, pk2, pk3]`
    connection.run(
        r.db(dbname)
         .table('bigchain')
         .index_create('outputs',
                       r.row['block']['transactions']
                        .concat_map(lambda tx: tx['outputs']['public_keys'])
                        .reduce(lambda l, r: l + r), multi=True))

    # secondary index on inputs/transaction links (transaction_id, output)
    connection.run(
        r.db(dbname)
         .table('bigchain')
         .index_create('inputs',
                       r.row['block']['transactions']
                        .concat_map(lambda tx: tx['inputs']['fulfills'])
                        .with_fields('transaction_id', 'output_index')
                        .map(lambda fulfills: [fulfills['transaction_id'],
                                               fulfills['output_index']]),
                       multi=True))

    # wait for rethinkdb to finish creating secondary indexes
    connection.run(
        r.db(dbname)
        .table('bigchain')
        .index_wait())


def create_backlog_secondary_index(connection, dbname):
    logger.info('Create `backlog` secondary index.')

    # compound index to read transactions from the backlog per assignee
    connection.run(
        r.db(dbname)
        .table('backlog')
        .index_create('assignee__transaction_timestamp', [r.row['assignee'], r.row['assignment_timestamp']]))

    # wait for rethinkdb to finish creating secondary indexes
    connection.run(
        r.db(dbname)
        .table('backlog')
        .index_wait())


def create_votes_secondary_index(connection, dbname):
    logger.info('Create `votes` secondary index.')

    # compound index to order votes by block id and node
    connection.run(
        r.db(dbname)
        .table('votes')
        .index_create('block_and_voter', [r.row['vote']['voting_for_block'], r.row['node_pubkey']]))

    # wait for rethinkdb to finish creating secondary indexes
    connection.run(
        r.db(dbname)
        .table('votes')
        .index_wait())
