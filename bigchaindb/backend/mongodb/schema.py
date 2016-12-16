"""Utils to initialize and drop the database."""

import logging

from pymongo import ASCENDING, DESCENDING

from bigchaindb import backend
from bigchaindb.common import exceptions
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.mongodb.connection import MongoDBConnection


logger = logging.getLogger(__name__)
register_schema = module_dispatch_registrar(backend.schema)


@register_schema(MongoDBConnection)
def create_database(conn, dbname):
    if dbname in conn.conn.database_names():
        raise exceptions.DatabaseAlreadyExists('Database `{}` already exists'
                                               .format(dbname))

    logger.info('Create database `%s`.', dbname)
    # TODO: read and write concerns can be declared here
    conn.conn.get_database(dbname)


@register_schema(MongoDBConnection)
def create_tables(conn, dbname):
    for table_name in ['bigchain', 'backlog', 'votes']:
        logger.info('Create `%s` table.', table_name)
        # create the table
        # TODO: read and write concerns can be declared here
        conn.conn[dbname].create_collection(table_name)


@register_schema(MongoDBConnection)
def create_indexes(conn, dbname):
    create_bigchain_secondary_index(conn, dbname)
    create_backlog_secondary_index(conn, dbname)
    create_votes_secondary_index(conn, dbname)


@register_schema(MongoDBConnection)
def drop_database(conn, dbname):
    conn.conn.drop_database(dbname)


def create_bigchain_secondary_index(conn, dbname):
    logger.info('Create `bigchain` secondary index.')

    # to select blocks by id
    conn.conn[dbname]['bigchain'].create_index('id', name='block_id')

    # to order blocks by timestamp
    conn.conn[dbname]['bigchain'].create_index([('block.timestamp', ASCENDING)],
                                          name='block_timestamp')

    # to query the bigchain for a transaction id, this field is unique
    conn.conn[dbname]['bigchain'].create_index('block.transactions.id',
                                          name='transaction_id', unique=True)

    # secondary index for payload data by UUID, this field is unique
    conn.conn[dbname]['bigchain']\
        .create_index('block.transactions.transaction.metadata.id',
                      name='metadata_id', unique=True)

    # secondary index for asset uuid, this field is unique
    conn.conn[dbname]['bigchain']\
        .create_index('block.transactions.transaction.asset.id',
                      name='asset_id', unique=True)

    # compound index on fulfillment and transactions id
    conn.conn[dbname]['bigchain']\
        .create_index([('block.transactions.transaction.fulfillments.txid',
                        ASCENDING),
                       ('block.transactions.transaction.fulfillments.cid',
                        ASCENDING)],
                      name='tx_and_fulfillment')


def create_backlog_secondary_index(conn, dbname):
    logger.info('Create `backlog` secondary index.')

    # to order transactions by timestamp
    conn.conn[dbname]['backlog']\
            .create_index([('transaction.timestamp', ASCENDING)],
                          name='transaction_timestamp')

    # compound index to read transactions from the backlog per assignee
    conn.conn[dbname]['backlog']\
        .create_index([('assignee', ASCENDING),
                       ('assignment_timestamp', DESCENDING)],
                      name='assignee__transaction_timestamp')


def create_votes_secondary_index(conn, dbname):
    logger.info('Create `votes` secondary index.')

    # index on block id to quickly poll
    conn.conn[dbname]['votes'].create_index('vote.voting_for_block',
                                       name='voting_for')

    # is the first index redundant then?
    # compound index to order votes by block id and node
    conn.conn[dbname]['votes']\
            .create_index([('vote.voting_for_block', ASCENDING),
                           ('node_pubkey', ASCENDING)],
                          name='block_and_voter')
