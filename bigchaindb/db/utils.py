"""Utils to initialize and drop the database."""

import time
import logging

from bigchaindb.common import exceptions
import rethinkdb as r

import bigchaindb


logger = logging.getLogger(__name__)


class Connection:
    """This class is a proxy to run queries against the database,
    it is:
    - lazy, since it creates a connection only when needed
    - resilient, because before raising exceptions it tries
      more times to run the query or open a connection.
    """

    def __init__(self, host=None, port=None, db=None, max_tries=3):
        """Create a new Connection instance.

        Args:
            host (str, optional): the host to connect to.
            port (int, optional): the port to connect to.
            db (str, optional): the database to use.
            max_tries (int, optional): how many tries before giving up.
        """

        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.db = db or bigchaindb.config['database']['name']
        self.max_tries = max_tries
        self.conn = None

    def run(self, query):
        """Run a query.

        Args:
            query: the RethinkDB query.
        """

        if self.conn is None:
            self._connect()

        for i in range(self.max_tries):
            try:
                return query.run(self.conn)
            except r.ReqlDriverError as exc:
                if i + 1 == self.max_tries:
                    raise
                else:
                    self._connect()

    def _connect(self):
        for i in range(self.max_tries):
            try:
                self.conn = r.connect(host=self.host, port=self.port,
                                      db=self.db)
            except r.ReqlDriverError as exc:
                if i + 1 == self.max_tries:
                    raise
                else:
                    time.sleep(2**i)


def get_backend(host=None, port=None, db=None):
    '''Get a backend instance.'''

    from bigchaindb.db.backends import rethinkdb

    # NOTE: this function will be re-implemented when we have real
    # multiple backends to support. Right now it returns the RethinkDB one.
    return rethinkdb.RethinkDBBackend(host=host or bigchaindb.config['database']['host'],
                                      port=port or bigchaindb.config['database']['port'],
                                      db=db or bigchaindb.config['database']['name'])


def get_conn():
    '''Get the connection to the database.'''

    return r.connect(host=bigchaindb.config['database']['host'],
                     port=bigchaindb.config['database']['port'],
                     db=bigchaindb.config['database']['name'])


def get_database_name():
    return bigchaindb.config['database']['name']


def create_database(conn, dbname):
    if r.db_list().contains(dbname).run(conn):
        raise exceptions.DatabaseAlreadyExists('Database `{}` already exists'.format(dbname))

    logger.info('Create database `%s`.', dbname)
    r.db_create(dbname).run(conn)


def create_table(conn, dbname, table_name):
    logger.info('Create `%s` table.', table_name)
    # create the table
    r.db(dbname).table_create(table_name).run(conn)


def create_bigchain_secondary_index(conn, dbname):
    logger.info('Create `bigchain` secondary index.')
    # to order blocks by timestamp
    r.db(dbname).table('bigchain')\
        .index_create('block_timestamp', r.row['block']['timestamp'])\
        .run(conn)
    # to query the bigchain for a transaction id
    r.db(dbname).table('bigchain')\
        .index_create('transaction_id',
                      r.row['block']['transactions']['id'], multi=True)\
        .run(conn)
    # secondary index for payload data by UUID
    r.db(dbname).table('bigchain')\
        .index_create('metadata_id',
                      r.row['block']['transactions']['transaction']['metadata']['id'], multi=True)\
        .run(conn)
    # secondary index for asset uuid
    r.db(dbname).table('bigchain')\
                .index_create('asset_id',
                              r.row['block']['transactions']['transaction']['asset']['id'], multi=True)\
                .run(conn)

    # wait for rethinkdb to finish creating secondary indexes
    r.db(dbname).table('bigchain').index_wait().run(conn)


def create_backlog_secondary_index(conn, dbname):
    logger.info('Create `backlog` secondary index.')
    # compound index to read transactions from the backlog per assignee
    r.db(dbname).table('backlog')\
        .index_create('assignee__transaction_timestamp',
                      [r.row['assignee'], r.row['assignment_timestamp']])\
        .run(conn)

    # wait for rethinkdb to finish creating secondary indexes
    r.db(dbname).table('backlog').index_wait().run(conn)


def create_votes_secondary_index(conn, dbname):
    logger.info('Create `votes` secondary index.')
    # compound index to order votes by block id and node
    r.db(dbname).table('votes')\
        .index_create('block_and_voter',
                      [r.row['vote']['voting_for_block'],
                       r.row['node_pubkey']])\
        .run(conn)

    # wait for rethinkdb to finish creating secondary indexes
    r.db(dbname).table('votes').index_wait().run(conn)


def init_database():
    conn = get_conn()
    dbname = get_database_name()
    create_database(conn, dbname)

    table_names = ['bigchain', 'backlog', 'votes']
    for table_name in table_names:
        create_table(conn, dbname, table_name)

    create_bigchain_secondary_index(conn, dbname)
    create_backlog_secondary_index(conn, dbname)
    create_votes_secondary_index(conn, dbname)


def init():
    # Try to access the keypair, throws an exception if it does not exist
    b = bigchaindb.Bigchain()

    init_database()

    logger.info('Create genesis block.')
    b.create_genesis_block()
    logger.info('Done, have fun!')


def drop(assume_yes=False):
    conn = get_conn()
    dbname = bigchaindb.config['database']['name']
    if assume_yes:
        response = 'y'

    else:
        response = input('Do you want to drop `{}` database? [y/n]: '.format(dbname))

    if response == 'y':
        try:
            logger.info('Drop database `%s`', dbname)
            r.db_drop(dbname).run(conn)
            logger.info('Done.')
        except r.ReqlOpFailedError:
            raise exceptions.DatabaseDoesNotExist('Database `{}` does not exist'.format(dbname))

    else:
        logger.info('Drop aborted')
