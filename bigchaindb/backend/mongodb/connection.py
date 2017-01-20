import time
import logging

from pymongo import MongoClient
from pymongo import errors

import bigchaindb
from bigchaindb.common import exceptions
from bigchaindb.backend.connection import Connection

logger = logging.getLogger(__name__)


class MongoDBConnection(Connection):

    def __init__(self, host=None, port=None, dbname=None, max_tries=3,
                 replicaset=None):
        """Create a new Connection instance.

        Args:
            host (str, optional): the host to connect to.
            port (int, optional): the port to connect to.
            dbname (str, optional): the database to use.
            max_tries (int, optional): how many tries before giving up.
            replicaset (str, optional): the name of the replica set to
                                        connect to.
        """

        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.replicaset = replicaset or bigchaindb.config['database']['replicaset']
        self.dbname = dbname or bigchaindb.config['database']['name']
        self.max_tries = max_tries
        self.connection = None

    @property
    def conn(self):
        if self.connection is None:
            self._connect()
        return self.connection

    @property
    def db(self):
        return self.conn[self.dbname]

    def _connect(self):
        # we should only return a connection if the replica set is
        # initialized. initialize_replica_set will check if the
        # replica set is initialized else it will initialize it.
        initialize_replica_set()

        for i in range(self.max_tries):
            try:
                self.connection = MongoClient(self.host, self.port,
                                              replicaset=self.replicaset)
            except errors.ConnectionFailure:
                if i + 1 == self.max_tries:
                    raise
                else:
                    time.sleep(2**i)


def initialize_replica_set():
    """Initialize a replica set. If already initialized skip."""

    # Setup a MongoDB connection
    # The reason we do this instead of `backend.connect` is that
    # `backend.connect` will connect you to a replica set but this fails if
    # you try to connect to a replica set that is not yet initialized
    conn = MongoClient(host=bigchaindb.config['database']['host'],
                       port=bigchaindb.config['database']['port'])
    _check_replica_set(conn)
    host = '{}:{}'.format(bigchaindb.config['database']['host'],
                          bigchaindb.config['database']['port'])
    config = {'_id': bigchaindb.config['database']['replicaset'],
              'members': [{'_id': 0, 'host': host}]}

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
