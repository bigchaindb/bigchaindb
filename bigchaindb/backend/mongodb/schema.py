"""Utils to initialize and drop the database."""

import time
import logging

from pymongo import ASCENDING, DESCENDING
from pymongo import errors

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

    # initialize the replica set
    initialize_replica_set(conn)


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
        .create_index('block.transactions.transaction.asset.id',
                      name='asset_id')


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


def initialize_replica_set(conn):
    """Initialize a replica set. If already initialized skip."""
    replica_set_name = _get_replica_set_name(conn)
    config = {'_id': replica_set_name,
              'members': [{'_id': 0, 'host': 'localhost:27017'}]}

    try:
        conn.conn.admin.command('replSetInitiate', config)
    except errors.OperationFailure as exc_info:
        if exc_info.details['codeName'] == 'AlreadyInitialized':
            logger.info('Replica set already initialized')
            return
        raise
    else:
        _wait_for_replica_set_initialization(conn)
        logger.info('Initialized replica set')


def _get_replica_set_name(conn):
    """Checks if the replSet option was enabled either through the command
       line option or config file.

       Note:
           The setting we are looking for will have a different name depending
           if it was set by the config file (`replSetName`) or by command
           line arguments (`replSet`).

       Returns:
           The replica set name if enabled.

        Raise:
            :exc:`~ConfigurationError`: If mongod was not started with the
            replSet option.
    """
    options = conn.conn.admin.command('getCmdLineOpts')
    try:
        repl_opts = options['parsed']['replication']
        return repl_opts.get('replSetName', None) or repl_opts['replSet']
    except KeyError:
        raise exceptions.ConfigurationError('mongod was not started with'
                                            ' the replSet option.')


def _wait_for_replica_set_initialization(conn):
    """Wait for a replica set to finish initialization.

    If a replica set is being initialized for the first time it takes some
    time. Nodes need to discover each other and an election needs to take
    place. During this time the database is not writable so we need to wait
    before continuing with the rest of the initialization
    """

    # I did not find a better way to do this for now.
    # To check if the database is ready we will poll the mongodb logs until
    # we find the line that says the database is ready
    logger.info('Waiting for mongodb replica set initialization')
    while True:
        logs = conn.conn.admin.command('getLog', 'rs')['log']
        if any('database writes are now permitted' in line for line in logs):
                return
        time.sleep(0.1)
