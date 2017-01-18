"""Utils to initialize and drop the database."""

import time
import logging

from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
from pymongo import errors

import bigchaindb
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


def initialize_replica_set():
    """Initialize a replica set. If already initialized skip."""

    # Setup a MongoDB connection
    # The reason we do this instead of `backend.connect` is that
    # `backend.connect` will connect you to a replica set but this fails if
    # you try to connect to a replica set that is not yet initialized
    conn = MongoClient(host=bigchaindb.config['database']['host'],
                       port=bigchaindb.config['database']['port'])
    _check_replica_set(conn)
    config = {'_id': bigchaindb.config['database']['replicaset'],
              'members': [{'_id': 0, 'host': 'localhost:27017'}]}

    try:
        conn.admin.command('replSetInitiate', config)
    except errors.OperationFailure as exc_info:
        if exc_info.details['codeName'] == 'AlreadyInitialized':
            return
        raise
    else:
        _wait_for_replica_set_initialization(conn)
        logger.info('Initialized replica set')


def _check_replica_set(conn):
    """Checks if the replSet option was enabled either through the command
       line option or config file and if it matches the one provided by
       bigchaindb configuration.

       Note:
           The setting we are looking for will have a different name depending
           if it was set by the config file (`replSetName`) or by command
           line arguments (`replSet`).

        Raise:
            :exc:`~ConfigurationError`: If mongod was not started with the
            replSet option.
    """
    options = conn.admin.command('getCmdLineOpts')
    try:
        repl_opts = options['parsed']['replication']
        repl_set_name = repl_opts.get('replSetName', None) or repl_opts['replSet']
    except KeyError:
        raise exceptions.ConfigurationError('mongod was not started with'
                                            ' the replSet option.')

    bdb_repl_set_name = bigchaindb.config['database']['replicaset']
    if repl_set_name != bdb_repl_set_name:
        raise exceptions.ConfigurationError('The replicaset configuration of '
                                            'bigchaindb (`{}`) needs to match '
                                            'the replica set name from MongoDB'
                                            ' (`{}`)'
                                            .format(bdb_repl_set_name,
                                                    repl_set_name))


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
        logs = conn.admin.command('getLog', 'rs')['log']
        if any('database writes are now permitted' in line for line in logs):
                return
        time.sleep(0.1)
