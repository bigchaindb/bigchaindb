"""
Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""

import os
import copy
import random

import pytest

from bigchaindb.common import crypto

TEST_DB_NAME = 'bigchain_test'

USER2_SK, USER2_PK = crypto.generate_key_pair()

# Test user. inputs will be created for this user. Cryptography Keys
USER_PRIVATE_KEY = '8eJ8q9ZQpReWyQT5aFCiwtZ5wDZC4eDnCen88p3tQ6ie'
USER_PUBLIC_KEY = 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE'


def pytest_addoption(parser):
    from bigchaindb.backend import connection

    backends = ', '.join(connection.BACKENDS.keys())
    parser.addoption(
        '--database-backend',
        action='store',
        default=os.environ.get('BIGCHAINDB_DATABASE_BACKEND', 'rethinkdb'),
        help='Defines the backend to use (available: {})'.format(backends),
    )


def pytest_ignore_collect(path, config):
    from bigchaindb.backend.connection import BACKENDS
    path = str(path)

    if os.path.isdir(path):
        dirname = os.path.split(path)[1]
        if dirname in BACKENDS.keys() and dirname != config.getoption('--database-backend'):
            print('Ignoring unrequested backend test dir: ', path)
            return True


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'bdb(): Mark the test as needing BigchainDB, i.e. a database with '
        'the three tables: "backlog", "bigchain", "votes". BigchainDB will '
        'be configured such that the database and tables are available for an '
        'entire test session. For distributed tests, the database name will '
        'be suffixed with the process identifier, e.g.: "bigchain_test_gw0", '
        'to ensure that each process session has its own separate database.'
    )
    config.addinivalue_line(
        'markers',
        'genesis(): Mark the test as needing a genesis block in place. The '
        'prerequisite steps of configuration and database setup are taken '
        'care of at session scope (if needed), prior to creating the genesis '
        'block. The genesis block has function scope: it is destroyed after '
        'each test function/method.'
    )


@pytest.fixture(autouse=True)
def _bdb_marker(request):
    if request.keywords.get('bdb', None):
        request.getfixturevalue('_bdb')


@pytest.fixture(autouse=True)
def _genesis_marker(request):
    if request.keywords.get('genesis', None):
        request.getfixturevalue('_genesis')


@pytest.fixture(autouse=True)
def _restore_config(_configure_bigchaindb):
    from bigchaindb import config, config_utils
    config_before_test = copy.deepcopy(config)
    yield
    config_utils.set_config(config_before_test)


@pytest.fixture
def _restore_dbs(request):
    from bigchaindb.backend import connect, schema
    from bigchaindb.common.exceptions import DatabaseDoesNotExist
    from .utils import list_dbs
    conn = connect()
    dbs_before_test = list_dbs(conn)
    yield
    dbs_after_test = list_dbs(conn)
    dbs_to_delete = (
        db for db in set(dbs_after_test) - set(dbs_before_test)
        if TEST_DB_NAME not in db
    )
    print(dbs_to_delete)
    for db in dbs_to_delete:
        try:
            schema.drop_database(conn, db)
        except DatabaseDoesNotExist:
            pass


@pytest.fixture(scope='session')
def _configure_bigchaindb(request):
    from bigchaindb import config_utils
    test_db_name = TEST_DB_NAME
    # Put a suffix like _gw0, _gw1 etc on xdist processes
    xdist_suffix = getattr(request.config, 'slaveinput', {}).get('slaveid')
    if xdist_suffix:
        test_db_name = '{}_{}'.format(TEST_DB_NAME, xdist_suffix)
    config = {
        'database': {
            'name': test_db_name,
            'backend': request.config.getoption('--database-backend'),
        },
        'keypair': {
            'private': '31Lb1ZGKTyHnmVK3LUMrAUrPNfd4sE2YyBt3UA4A25aA',
            'public': '4XYfCbabAWVUCbjTmRTFEu2sc3dFEdkse4r6X498B1s8',
        }
    }
    # FIXME
    if config['database']['backend'] == 'mongodb':
        # not a great way to do this
        config['database']['port'] = 27017
    config_utils.set_config(config)


@pytest.fixture(scope='session')
def _setup_database(_configure_bigchaindb):
    from bigchaindb import config
    from bigchaindb.backend import connect, schema
    from bigchaindb.backend.mongodb.schema import initialize_replica_set
    from bigchaindb.common.exceptions import DatabaseDoesNotExist
    print('Initializing test db')
    dbname = config['database']['name']
    conn = connect()

    # if we are setting up mongodb for the first time we need to make sure
    # that the replica set is initialized before doing any operation in the
    # database
    if config['database']['backend'] == 'mongodb':
        initialize_replica_set(conn)

    try:
        schema.drop_database(conn, dbname)
    except DatabaseDoesNotExist:
        pass

    schema.init_database(conn)
    print('Finishing init database')

    yield

    print('Deleting `{}` database'.format(dbname))
    conn = connect()
    try:
        schema.drop_database(conn, dbname)
    except DatabaseDoesNotExist:
        pass

    print('Finished deleting `{}`'.format(dbname))


@pytest.fixture
def _bdb(_setup_database, _configure_bigchaindb):
    from bigchaindb import config
    from bigchaindb.backend import connect
    from bigchaindb.backend.admin import get_config
    from bigchaindb.backend.schema import TABLES
    from .utils import flush_db, update_table_config
    conn = connect()
    # TODO remove condition once the mongodb implementation is done
    if config['database']['backend'] == 'rethinkdb':
        table_configs_before = {
            t: get_config(conn, table=t) for t in TABLES
        }
    yield
    dbname = config['database']['name']
    flush_db(conn, dbname)
    # TODO remove condition once the mongodb implementation is done
    if config['database']['backend'] == 'rethinkdb':
        for t, c in table_configs_before.items():
            update_table_config(conn, t, **c)


@pytest.fixture
def _genesis(_bdb, genesis_block):
    # TODO for precision's sake, delete the block once the test is done. The
    # deletion is done indirectly via the teardown code of _bdb but explicit
    # deletion of the block would make things clearer. E.g.:
    # yield
    # tests.utils.delete_genesis_block(conn, dbname)
    pass


# We need this function to avoid loading an existing
# conf file located in the home of the user running
# the tests. If it's too aggressive we can change it
# later.
@pytest.fixture
def ignore_local_config_file(monkeypatch):
    def mock_file_config(filename=None):
        raise FileNotFoundError()

    monkeypatch.setattr('bigchaindb.config_utils.file_config',
                        mock_file_config)


@pytest.fixture
def user_sk():
    return USER_PRIVATE_KEY


@pytest.fixture
def user_pk():
    return USER_PUBLIC_KEY


@pytest.fixture
def user2_sk():
    return USER2_SK


@pytest.fixture
def user2_pk():
    return USER2_PK


@pytest.fixture
def b():
    from bigchaindb import Bigchain
    return Bigchain()


@pytest.fixture
def create_tx(b, user_pk):
    from bigchaindb.models import Transaction
    return Transaction.create([b.me], [([user_pk], 1)])


@pytest.fixture
def signed_create_tx(b, create_tx):
    return create_tx.sign([b.me_private])


@pytest.fixture
def signed_transfer_tx(signed_create_tx, user_pk, user_sk):
    from bigchaindb.models import Transaction
    inputs = signed_create_tx.to_inputs()
    tx = Transaction.transfer(inputs, [([user_pk], 1)], asset_id=signed_create_tx.id)
    return tx.sign([user_sk])


@pytest.fixture
def structurally_valid_vote():
    return {
        'node_pubkey': 'c' * 44,
        'signature': 'd' * 86,
        'vote': {
            'voting_for_block': 'a' * 64,
            'previous_block': 'b' * 64,
            'is_block_valid': False,
            'invalid_reason': None,
            'timestamp': '1111111111'
        }
    }


@pytest.fixture
def genesis_block(b):
    return b.create_genesis_block()


@pytest.fixture
def inputs(user_pk, b, genesis_block):
    from bigchaindb.models import Transaction

    # create blocks with transactions for `USER` to spend
    prev_block_id = genesis_block.id
    for block in range(4):
        transactions = [
            Transaction.create(
                [b.me],
                [([user_pk], 1)],
                metadata={'msg': random.random()},
            ).sign([b.me_private])
            for _ in range(10)
        ]
        block = b.create_block(transactions)
        b.write_block(block)

        # vote the blocks valid, so that the inputs are valid
        vote = b.vote(block.id, prev_block_id, True)
        prev_block_id = block.id
        b.write_vote(vote)


@pytest.fixture
def inputs_shared(user_pk, user2_pk, genesis_block):
    from bigchaindb.models import Transaction

    # create blocks with transactions for `USER` to spend
    prev_block_id = genesis_block.id
    for block in range(4):
        transactions = [
            Transaction.create(
                [b.me],
                [user_pk, user2_pk],
                metadata={'msg': random.random()},
            ).sign([b.me_private])
            for _ in range(10)
        ]
        block = b.create_block(transactions)
        b.write_block(block)

        # vote the blocks valid, so that the inputs are valid
        vote = b.vote(block.id, prev_block_id, True)
        prev_block_id = block.id
        b.write_vote(vote)


@pytest.fixture
def dummy_db(request):
    from bigchaindb.backend import connect, schema
    from bigchaindb.common.exceptions import (DatabaseDoesNotExist,
                                              DatabaseAlreadyExists)
    conn = connect()
    dbname = request.fixturename
    xdist_suffix = getattr(request.config, 'slaveinput', {}).get('slaveid')
    if xdist_suffix:
        dbname = '{}_{}'.format(dbname, xdist_suffix)
    try:
        schema.init_database(conn, dbname)
    except DatabaseAlreadyExists:
        schema.drop_database(conn, dbname)
        schema.init_database(conn, dbname)
    yield dbname
    try:
        schema.drop_database(conn, dbname)
    except DatabaseDoesNotExist:
        pass


@pytest.fixture
def not_yet_created_db(request):
    from bigchaindb.backend import connect, schema
    from bigchaindb.common.exceptions import DatabaseDoesNotExist
    conn = connect()
    dbname = request.fixturename
    xdist_suffix = getattr(request.config, 'slaveinput', {}).get('slaveid')
    if xdist_suffix:
        dbname = '{}_{}'.format(dbname, xdist_suffix)
    try:
        schema.drop_database(conn, dbname)
    except DatabaseDoesNotExist:
        pass
    yield dbname
    try:
        schema.drop_database(conn, dbname)
    except DatabaseDoesNotExist:
        pass


@pytest.fixture
def db_config():
    from bigchaindb import config
    return config['database']


@pytest.fixture
def db_host(db_config):
    return db_config['host']


@pytest.fixture
def db_port(db_config):
    return db_config['port']


@pytest.fixture
def db_name(db_config):
    return db_config['name']


@pytest.fixture
def db_conn():
    from bigchaindb.backend import connect
    return connect()
