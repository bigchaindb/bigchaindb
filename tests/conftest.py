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
        'bdb(): use bigchaindb')


@pytest.fixture(autouse=True)
def _bdb_marker(request):
    if request.keywords.get('bdb', None):
        request.getfixturevalue('_bdb')


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
    from bigchaindb.common.exceptions import DatabaseDoesNotExist
    print('Initializing test db')
    db_name = config['database']['name']
    conn = connect()

    try:
        schema.drop_database(conn, db_name)
    except DatabaseDoesNotExist:
        pass

    schema.init_database(conn)
    print('Finishing init database')

    yield

    print('Deleting `{}` database'.format(db_name))
    conn = connect()
    try:
        schema.drop_database(conn, db_name)
    except DatabaseDoesNotExist:
        pass

    print('Finished deleting `{}`'.format(db_name))


@pytest.fixture
def _bdb(_setup_database, _configure_bigchaindb):
    yield
    from bigchaindb import config
    from bigchaindb.backend import connect
    from .utils import flush_db
    dbname = config['database']['name']
    conn = connect()
    flush_db(conn, dbname)


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
    from bigchaindb.common.transaction import AssetLink
    from bigchaindb.models import Transaction
    inputs = signed_create_tx.to_inputs()
    tx = Transaction.transfer(inputs,
                              [([user_pk], 1)],
                              AssetLink(signed_create_tx.id))
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
def inputs(user_pk):
    from bigchaindb import Bigchain
    from bigchaindb.models import Transaction
    from bigchaindb.common.exceptions import GenesisBlockAlreadyExistsError
    # 1. create the genesis block
    b = Bigchain()
    try:
        g = b.create_genesis_block()
    except GenesisBlockAlreadyExistsError:
        pass

    # 2. create blocks with transactions for `USER` to spend
    prev_block_id = g.id
    for block in range(4):
        transactions = [
            Transaction.create([b.me], [([user_pk], 1)],
                               metadata={'msg': random.random()})
                       .sign([b.me_private])
            for _ in range(10)
        ]
        block = b.create_block(transactions)
        b.write_block(block)

        # 3. vote the blocks valid, so that the inputs are valid
        vote = b.vote(block.id, prev_block_id, True)
        prev_block_id = block.id
        b.write_vote(vote)


@pytest.fixture
def inputs_shared(user_pk, user2_pk):
    from bigchaindb import Bigchain
    from bigchaindb.models import Transaction
    from bigchaindb.common.exceptions import GenesisBlockAlreadyExistsError
    # 1. create the genesis block
    b = Bigchain()
    try:
        g = b.create_genesis_block()
    except GenesisBlockAlreadyExistsError:
        pass

    # 2. create blocks with transactions for `USER` to spend
    prev_block_id = g.id
    for block in range(4):
        transactions = [
            Transaction.create([b.me], [user_pk, user2_pk],
                               metadata={'msg': random.random()})
                       .sign([b.me_private])
            for _ in range(10)
        ]
        block = b.create_block(transactions)
        b.write_block(block)

        # 3. vote the blocks valid, so that the inputs are valid
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
        schema.create_database(conn, dbname)
    except DatabaseAlreadyExists:
        schema.drop_database(conn, dbname)
        schema.create_database(conn, dbname)
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
