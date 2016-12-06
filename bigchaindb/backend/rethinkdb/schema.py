"""Utils to initialize and drop the database."""

import logging

import rethinkdb as r

from bigchaindb import backend
from bigchaindb.common import exceptions
from bigchaindb.backend.utils import make_module_dispatch_registrar
from bigchaindb.backend.rethinkdb.connection import RethinkDBConnection


logger = logging.getLogger(__name__)
register_schema = make_module_dispatch_registrar(backend.schema)


@register_schema(RethinkDBConnection)
def create_database(connection, name):
    if connection.run(r.db_list().contains(name)):
        raise exceptions.DatabaseAlreadyExists('Database `{}` already exists'.format(name))

    logger.info('Create database `%s`.', name)
    connection.run(r.db_create(name))


@register_schema(RethinkDBConnection)
def create_tables(connection, name):
    for table_name in ['bigchain', 'backlog', 'votes']:
        logger.info('Create `%s` table.', table_name)
        connection.run(r.db(name).table_create(table_name))


@register_schema(RethinkDBConnection)
def create_indexes(connection, name):
    create_bigchain_secondary_index(connection, name)
    create_backlog_secondary_index(connection, name)
    create_votes_secondary_index(connection, name)


@register_schema(RethinkDBConnection)
def drop_database(connection, name):
    try:
        logger.info('Drop database `%s`', name)
        connection.run(r.db_drop(name))
        logger.info('Done.')
    except r.ReqlOpFailedError:
        raise exceptions.DatabaseDoesNotExist('Database `{}` does not exist'.format(name))


def create_bigchain_secondary_index(connection, name):
    logger.info('Create `bigchain` secondary index.')

    # to order blocks by timestamp
    connection.run(
        r.db(name)
        .table('bigchain')
        .index_create('block_timestamp', r.row['block']['timestamp']))

    # to query the bigchain for a transaction id
    connection.run(
        r.db(name)
        .table('bigchain')
        .index_create('transaction_id', r.row['block']['transactions']['id'], multi=True))

    # secondary index for payload data by UUID
    connection.run(
        r.db(name)
        .table('bigchain')
        .index_create('metadata_id', r.row['block']['transactions']['transaction']['metadata']['id'], multi=True))

    # secondary index for asset uuid
    connection.run(
        r.db(name)
        .table('bigchain')
        .index_create('asset_id', r.row['block']['transactions']['transaction']['asset']['id'], multi=True))

    # wait for rethinkdb to finish creating secondary indexes
    connection.run(
        r.db(name)
        .table('bigchain')
        .index_wait())


def create_backlog_secondary_index(connection, name):
    logger.info('Create `backlog` secondary index.')

    # compound index to read transactions from the backlog per assignee
    connection.run(
        r.db(name)
        .table('backlog')
        .index_create('assignee__transaction_timestamp', [r.row['assignee'], r.row['assignment_timestamp']]))

    # wait for rethinkdb to finish creating secondary indexes
    connection.run(
        r.db(name)
        .table('backlog')
        .index_wait())


def create_votes_secondary_index(connection, name):
    logger.info('Create `votes` secondary index.')

    # compound index to order votes by block id and node
    connection.run(
        r.db(name)
        .table('votes')
        .index_create('block_and_voter', [r.row['vote']['voting_for_block'], r.row['node_pubkey']]))

    # wait for rethinkdb to finish creating secondary indexes
    connection.run(
        r.db(name)
        .table('votes')
        .index_wait())
