"""Utils to initialize and drop the database."""

import logging

import rethinkdb as r

import bigchaindb
from bigchaindb import exceptions


logger = logging.getLogger(__name__)


def get_conn():
    '''Get the connection to the database.'''

    return r.connect(bigchaindb.config['database']['host'],
                     bigchaindb.config['database']['port'])


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
        .index_create('payload_uuid',
                      r.row['block']['transactions']['transaction']['data']['uuid'], multi=True)\
        .run(conn)

    # wait for rethinkdb to finish creating secondary indexes
    r.db(dbname).table('bigchain').index_wait().run(conn)


def create_backlog_secondary_index(conn, dbname):
    logger.info('Create `backlog` secondary index.')
    # to order transactions by timestamp
    r.db(dbname).table('backlog')\
        .index_create('transaction_timestamp',
                      r.row['transaction']['timestamp'])\
        .run(conn)
    # compound index to read transactions from the backlog per assignee
    r.db(dbname).table('backlog')\
        .index_create('assignee__transaction_timestamp',
                      [r.row['assignee'], r.row['transaction']['timestamp']])\
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


def init():
    # Try to access the keypair, throws an exception if it does not exist
    b = bigchaindb.Bigchain()

    conn = get_conn()
    dbname = get_database_name()
    create_database(conn, dbname)

    table_names = ['bigchain', 'backlog', 'votes']
    for table_name in table_names:
        create_table(conn, dbname, table_name)
    create_bigchain_secondary_index(conn, dbname)
    create_backlog_secondary_index(conn, dbname)
    create_votes_secondary_index(conn, dbname)

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
