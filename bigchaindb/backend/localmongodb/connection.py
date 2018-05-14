import time
import logging
from ssl import CERT_REQUIRED

import pymongo

import bigchaindb
from bigchaindb.utils import Lazy
from bigchaindb.common.exceptions import ConfigurationError
from bigchaindb.backend.exceptions import (DuplicateKeyError,
                                           OperationError,
                                           ConnectionError)
from bigchaindb.backend.connection import Connection

logger = logging.getLogger(__name__)


class LocalMongoDBConnection(Connection):

    def __init__(self, replicaset=None, ssl=None, login=None, password=None,
                 ca_cert=None, certfile=None, keyfile=None,
                 keyfile_passphrase=None, crlfile=None, **kwargs):
        """Create a new Connection instance.

        Args:
            replicaset (str, optional): the name of the replica set to
                                        connect to.
            **kwargs: arbitrary keyword arguments provided by the
                configuration's ``database`` settings
        """

        super().__init__(**kwargs)
        self.replicaset = replicaset or bigchaindb.config['database'].get('replicaset')
        self.ssl = ssl if ssl is not None else bigchaindb.config['database'].get('ssl', False)
        self.login = login or bigchaindb.config['database'].get('login')
        self.password = password or bigchaindb.config['database'].get('password')
        self.ca_cert = ca_cert or bigchaindb.config['database'].get('ca_cert', None)
        self.certfile = certfile or bigchaindb.config['database'].get('certfile', None)
        self.keyfile = keyfile or bigchaindb.config['database'].get('keyfile', None)
        self.keyfile_passphrase = keyfile_passphrase or bigchaindb.config['database'].get('keyfile_passphrase', None)
        self.crlfile = crlfile or bigchaindb.config['database'].get('crlfile', None)

    @property
    def db(self):
        return self.conn[self.dbname]

    def query(self):
        return Lazy()

    def collection(self, name):
        """Return a lazy object that can be used to compose a query.

        Args:
            name (str): the name of the collection to query.
        """
        return self.query()[self.dbname][name]

    def run(self, query):
        try:
            try:
                return query.run(self.conn)
            except pymongo.errors.AutoReconnect as exc:
                logger.warning('Lost connection to the database, '
                               'retrying query.')
                return query.run(self.conn)
        except pymongo.errors.AutoReconnect as exc:
            raise ConnectionError from exc
        except pymongo.errors.DuplicateKeyError as exc:
            raise DuplicateKeyError from exc
        except pymongo.errors.OperationFailure as exc:
            print(f'DETAILS: {exc.details}')
            raise OperationError from exc

    def _connect(self):
        """Try to connect to the database.

        Raises:
            :exc:`~ConnectionError`: If the connection to the database
                fails.
            :exc:`~AuthenticationError`: If there is a OperationFailure due to
                Authentication failure after connecting to the database.
            :exc:`~ConfigurationError`: If there is a ConfigurationError while
                connecting to the database.
        """

        try:
            if self.replicaset:
                # we should only return a connection if the replica set is
                # initialized. initialize_replica_set will check if the
                # replica set is initialized else it will initialize it.
                initialize_replica_set(self.host,
                                       self.port,
                                       self.connection_timeout,
                                       self.dbname,
                                       self.ssl,
                                       self.login,
                                       self.password,
                                       self.ca_cert,
                                       self.certfile,
                                       self.keyfile,
                                       self.keyfile_passphrase,
                                       self.crlfile)

            # FYI: the connection process might raise a
            # `ServerSelectionTimeoutError`, that is a subclass of
            # `ConnectionFailure`.
            # The presence of ca_cert, certfile, keyfile, crlfile implies the
            # use of certificates for TLS connectivity.
            if self.ca_cert is None or self.certfile is None or \
                    self.keyfile is None or self.crlfile is None:
                client = pymongo.MongoClient(self.host,
                                             self.port,
                                             replicaset=self.replicaset,
                                             serverselectiontimeoutms=self.connection_timeout,
                                             ssl=self.ssl,
                                             **MONGO_OPTS)
                if self.login is not None and self.password is not None:
                    client[self.dbname].authenticate(self.login, self.password)
            else:
                logger.info('Connecting to MongoDB over TLS/SSL...')
                client = pymongo.MongoClient(self.host,
                                             self.port,
                                             replicaset=self.replicaset,
                                             serverselectiontimeoutms=self.connection_timeout,
                                             ssl=self.ssl,
                                             ssl_ca_certs=self.ca_cert,
                                             ssl_certfile=self.certfile,
                                             ssl_keyfile=self.keyfile,
                                             ssl_pem_passphrase=self.keyfile_passphrase,
                                             ssl_crlfile=self.crlfile,
                                             ssl_cert_reqs=CERT_REQUIRED,
                                             **MONGO_OPTS)
                if self.login is not None:
                    client[self.dbname].authenticate(self.login,
                                                     mechanism='MONGODB-X509')

            return client

        # `initialize_replica_set` might raise `ConnectionFailure`,
        # `OperationFailure` or `ConfigurationError`.
        except (pymongo.errors.ConnectionFailure,
                pymongo.errors.OperationFailure) as exc:
            logger.info('Exception in _connect(): {}'.format(exc))
            raise ConnectionError(str(exc)) from exc
        except pymongo.errors.ConfigurationError as exc:
            raise ConfigurationError from exc


MONGO_OPTS = {
    'socketTimeoutMS': 20000,
}


def initialize_replica_set(host, port, connection_timeout, dbname, ssl, login,
                           password, ca_cert, certfile, keyfile,
                           keyfile_passphrase, crlfile):
    """Initialize a replica set. If already initialized skip."""

    # Setup a MongoDB connection
    # The reason we do this instead of `backend.connect` is that
    # `backend.connect` will connect you to a replica set but this fails if
    # you try to connect to a replica set that is not yet initialized
    try:
        # The presence of ca_cert, certfile, keyfile, crlfile implies the
        # use of certificates for TLS connectivity.
        if ca_cert is None or certfile is None or keyfile is None or \
                crlfile is None:
            conn = pymongo.MongoClient(host,
                                       port,
                                       serverselectiontimeoutms=connection_timeout,
                                       ssl=ssl,
                                       **MONGO_OPTS)
            if login is not None and password is not None:
                conn[dbname].authenticate(login, password)
        else:
            logger.info('Connecting to MongoDB over TLS/SSL...')
            conn = pymongo.MongoClient(host,
                                       port,
                                       serverselectiontimeoutms=connection_timeout,
                                       ssl=ssl,
                                       ssl_ca_certs=ca_cert,
                                       ssl_certfile=certfile,
                                       ssl_keyfile=keyfile,
                                       ssl_pem_passphrase=keyfile_passphrase,
                                       ssl_crlfile=crlfile,
                                       ssl_cert_reqs=CERT_REQUIRED,
                                       **MONGO_OPTS)
            if login is not None:
                logger.info('Authenticating to the database...')
                conn[dbname].authenticate(login, mechanism='MONGODB-X509')

    except (pymongo.errors.ConnectionFailure,
            pymongo.errors.OperationFailure) as exc:
        logger.info('Exception in _connect(): {}'.format(exc))
        raise ConnectionError(str(exc)) from exc
    except pymongo.errors.ConfigurationError as exc:
        raise ConfigurationError from exc

    _check_replica_set(conn)
    host = '{}:{}'.format(bigchaindb.config['database']['host'],
                          bigchaindb.config['database']['port'])
    config = {'_id': bigchaindb.config['database']['replicaset'],
              'members': [{'_id': 0, 'host': host}]}

    try:
        conn.admin.command('replSetInitiate', config)
    except pymongo.errors.OperationFailure as exc_info:
        if exc_info.details['codeName'] == 'AlreadyInitialized':
            return
        raise
    else:
        _wait_for_replica_set_initialization(conn)
        logger.info('Initialized replica set')
    finally:
        if conn is not None:
            logger.info('Closing initial connection to MongoDB')
            conn.close()


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
        repl_set_name = repl_opts.get('replSetName', repl_opts.get('replSet'))
    except KeyError:
        raise ConfigurationError('mongod was not started with'
                                 ' the replSet option.')

    bdb_repl_set_name = bigchaindb.config['database']['replicaset']
    if repl_set_name != bdb_repl_set_name:
        raise ConfigurationError('The replicaset configuration of '
                                 'bigchaindb (`{}`) needs to match '
                                 'the replica set name from MongoDB'
                                 ' (`{}`)'.format(bdb_repl_set_name,
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
