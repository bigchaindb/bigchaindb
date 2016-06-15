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


def init():
    # Try to access the keypair, throws an exception if it does not exist
    b = bigchaindb.Bigchain()

    conn = get_conn()
    dbname = bigchaindb.config['database']['name']

    if r.db_list().contains(dbname).run(conn):
        raise exceptions.DatabaseAlreadyExists('Database `{}` already exists'.format(dbname))

    logger.info('Create:')
    logger.info(' - database `%s`', dbname)
    r.db_create(dbname).run(conn)

    logger.info(' - tables')
    # create the tables
    r.db(dbname).table_create('bigchain').run(conn)
    r.db(dbname).table_create('backlog').run(conn)

    logger.info(' - indexes')
    # create the secondary indexes
    # to order blocks by timestamp
    r.db(dbname).table('bigchain').index_create('block_timestamp', r.row['block']['timestamp']).run(conn)
    # to order blocks by block number
    r.db(dbname).table('bigchain').index_create('block_number', r.row['block']['block_number']).run(conn)
    # to order transactions by timestamp
    r.db(dbname).table('backlog').index_create('transaction_timestamp', r.row['transaction']['timestamp']).run(conn)
    # to query the bigchain for a transaction id
    r.db(dbname).table('bigchain').index_create('transaction_id',
                                                r.row['block']['transactions']['id'], multi=True).run(conn)
    # compound index to read transactions from the backlog per assignee
    r.db(dbname).table('backlog')\
        .index_create('assignee__transaction_timestamp', [r.row['assignee'], r.row['transaction']['timestamp']])\
        .run(conn)
    # secondary index for payload hash
    r.db(dbname).table('bigchain')\
        .index_create('payload_uuid', r.row['block']['transactions']['transaction']['data']['uuid'], multi=True)\
        .run(conn)

    # wait for rethinkdb to finish creating secondary indexes
    r.db(dbname).table('backlog').index_wait().run(conn)
    r.db(dbname).table('bigchain').index_wait().run(conn)

    logger.info(' - genesis block')
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
