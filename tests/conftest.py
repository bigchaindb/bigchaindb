"""
Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""

import os
import copy

import pytest

from bigchaindb.common import crypto


USER2_SK, USER2_PK = crypto.generate_key_pair()
DB_NAME = 'bigchain_test_{}'.format(os.getpid())

CONFIG = {
    'database': {
        'name': DB_NAME,
    },
    'keypair': {
        'private': '31Lb1ZGKTyHnmVK3LUMrAUrPNfd4sE2YyBt3UA4A25aA',
        'public': '4XYfCbabAWVUCbjTmRTFEu2sc3dFEdkse4r6X498B1s8',
    }
}

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


# We need this function to avoid loading an existing
# conf file located in the home of the user running
# the tests. If it's too aggressive we can change it
# later.
#@pytest.fixture(scope='function', autouse=True)
@pytest.fixture
def ignore_local_config_file(monkeypatch):
    def mock_file_config(filename=None):
        raise FileNotFoundError()

    monkeypatch.setattr('bigchaindb.config_utils.file_config',
                        mock_file_config)


#@pytest.fixture(scope='function', autouse=True)
@pytest.fixture
def restore_config(request, ignore_local_config_file, node_config):
    from bigchaindb import config_utils
    config_utils.set_config(node_config)


@pytest.fixture(scope='module')
def node_config(request):
    config = copy.deepcopy(CONFIG)
    config['database']['backend'] = request.config.getoption('--database-backend')
    return config


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
#def b(request, node_config):
def b(request, restore_config):
    #restore_config(request, node_config)
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
    tx = Transaction.transfer(inputs, [([user_pk], 1)], signed_create_tx.asset)
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
def setup_database(request, restore_config, node_config):
    from bigchaindb.backend import connect, schema
    from bigchaindb.common.exceptions import DatabaseDoesNotExist
    print('Initializing test db')
    db_name = node_config['database']['name']
    conn = connect()

    try:
        schema.drop_database(conn, db_name)
    except DatabaseDoesNotExist:
        pass

    schema.init_database(conn)

    print('Finishing init database')

    def fin():
        conn = connect()
        print('Deleting `{}` database'.format(db_name))
        try:
            schema.drop_database(conn, db_name)
        except DatabaseDoesNotExist:
            pass

        print('Finished deleting `{}`'.format(db_name))

    request.addfinalizer(fin)


@pytest.fixture
def inputs(user_pk, setup_database):
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
            Transaction.create([b.me], [([user_pk], 1)]).sign([b.me_private])
            for i in range(10)
        ]
        block = b.create_block(transactions)
        b.write_block(block)

        # 3. vote the blocks valid, so that the inputs are valid
        vote = b.vote(block.id, prev_block_id, True)
        prev_block_id = block.id
        b.write_vote(vote)


@pytest.fixture
def inputs_shared(user_pk, user2_pk, setup_database):
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
            Transaction.create(
                [b.me], [user_pk, user2_pk], payload={'i': i}).sign([b.me_private])
            for i in range(10)
        ]
        block = b.create_block(transactions)
        b.write_block(block)

        # 3. vote the blocks valid, so that the inputs are valid
        vote = b.vote(block.id, prev_block_id, True)
        prev_block_id = block.id
        b.write_vote(vote)
