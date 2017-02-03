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

    # to order blocks by timestamp
    conn.conn[dbname]['bigchain'].create_index([('block.timestamp',
                                                 ASCENDING)],
                                               name='block_timestamp')

    # to query the bigchain for a transaction id, this field is unique
    conn.conn[dbname]['bigchain'].create_index('block.transactions.id',
                                               name='transaction_id')

    # secondary index for asset uuid, this field is unique
    conn.conn[dbname]['bigchain']\
        .create_index('block.transactions.asset.id', name='asset_id')

    # secondary index on the public keys of outputs
    conn.conn[dbname]['bigchain']\
        .create_index('block.transactions.outputs.public_keys',
                      name='outputs')

    # secondary index on inputs/transaction links (txid, output)
    conn.conn[dbname]['bigchain']\
        .create_index([
            ('block.transactions.inputs.fulfills.txid', ASCENDING),
            ('block.transactions.inputs.fulfills.output', ASCENDING),
        ], name='inputs')


def create_backlog_secondary_index(conn, dbname):
    logger.info('Create `backlog` secondary index.')

    # secondary index on the transaction id with a uniqueness constraint
    # to make sure there are no duplicated transactions in the backlog
    conn.conn[dbname]['backlog'].create_index('id',
                                              name='transaction_id',
                                              unique=True)

    # compound index to read transactions from the backlog per assignee
    conn.conn[dbname]['backlog']\
        .create_index([('assignee', ASCENDING),
                       ('assignment_timestamp', DESCENDING)],
                      name='assignee__transaction_timestamp')


def create_votes_secondary_index(conn, dbname):
    logger.info('Create `votes` secondary index.')

    # is the first index redundant then?
    # compound index to order votes by block id and node
    conn.conn[dbname]['votes'].create_index([('vote.voting_for_block',
                                              ASCENDING),
                                             ('node_pubkey',
                                              ASCENDING)],
                                            name='block_and_voter')
