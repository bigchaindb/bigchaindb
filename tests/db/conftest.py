"""
Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""

import pytest
import rethinkdb as r

from bigchaindb import Bigchain
from bigchaindb.db import get_conn


NOOP = None


@pytest.fixture(autouse=True)
def restore_config(request, node_config):
    import bigchaindb.config_utils
    bigchaindb.config_utils.dict_config(node_config)


@pytest.fixture(scope='module', autouse=True)
def setup_database(request):
    print('Initializing test db')
    get_conn().repl()
    try:
        r.db_create('bigchain_test').run()
    except r.ReqlOpFailedError as e:
        if e.message == 'Database `bigchain_test` already exists.':
            r.db_drop('bigchain_test').run()
            r.db_create('bigchain_test').run()
        else:
            raise

    print('Finished initializing test db')

    # setup tables
    r.db('bigchain_test').table_create('bigchain').run()
    r.db('bigchain_test').table_create('backlog').run()
    # create the secondary indexes
    # to order blocks by timestamp
    r.db('bigchain_test').table('bigchain').index_create('block_timestamp', r.row['block']['timestamp']).run()
    # to order blocks by block number
    r.db('bigchain_test').table('bigchain').index_create('block_number', r.row['block']['block_number']).run()
    # to order transactions by timestamp
    r.db('bigchain_test').table('backlog').index_create('transaction_timestamp', r.row['transaction']['timestamp']).run()
    # compound index to read transactions from the backlog per assignee
    r.db('bigchain_test').table('backlog')\
        .index_create('assignee__transaction_timestamp', [r.row['assignee'], r.row['transaction']['timestamp']])\
        .run()

    def fin():
        print('Deleting `bigchain_test` database')
        get_conn().repl()
        try:
            r.db_drop('bigchain_test').run()
        except r.ReqlOpFailedError as e:
            if e.message != 'Database `bigchain_test` does not exist.':
                raise

        print('Finished deleting `bigchain_test`')

    request.addfinalizer(fin)


@pytest.fixture(scope='function', autouse=True)
def cleanup_tables(request):
    def fin():
        get_conn().repl()
        try:
            r.db('bigchain_test').table('bigchain').delete().run()
            r.db('bigchain_test').table('backlog').delete().run()
        except r.ReqlOpFailedError as e:
            if e.message != 'Database `bigchain_test` does not exist.':
                raise

    request.addfinalizer(fin)


@pytest.fixture
def b():
    return Bigchain()

