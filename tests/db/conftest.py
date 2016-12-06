"""
Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""

import pytest
import rethinkdb as r

from bigchaindb import Bigchain
from bigchaindb.backend import connect, schema
from bigchaindb.common import crypto
from bigchaindb.common.exceptions import DatabaseAlreadyExists


USER2_SK, USER2_PK = crypto.generate_key_pair()


@pytest.fixture(autouse=True)
def restore_config(request, node_config):
    from bigchaindb import config_utils
    config_utils.set_config(node_config)


@pytest.fixture(scope='module', autouse=True)
def setup_database(request, node_config):
    print('Initializing test db')
    db_name = node_config['database']['name']
    conn = connect()

    if conn.run(r.db_list().contains(db_name)):
        conn.run(r.db_drop(db_name))

    try:
        schema.init_database()
    except DatabaseAlreadyExists:
        print('Database already exists.')

    print('Finishing init database')

    def fin():
        print('Deleting `{}` database'.format(db_name))
        conn = connect()
        try:
            conn.run(r.db_drop(db_name))
        except r.ReqlOpFailedError as e:
            if e.message != 'Database `{}` does not exist.'.format(db_name):
                raise
        print('Finished deleting `{}`'.format(db_name))

    request.addfinalizer(fin)


@pytest.fixture(scope='function', autouse=True)
def cleanup_tables(request, node_config):
    db_name = node_config['database']['name']

    def fin():
        conn = connect()
        try:
            conn.run(r.db(db_name).table('bigchain').delete())
            conn.run(r.db(db_name).table('backlog').delete())
            conn.run(r.db(db_name).table('votes').delete())
        except r.ReqlOpFailedError as e:
            if e.message != 'Database `{}` does not exist.'.format(db_name):
                raise

    request.addfinalizer(fin)


@pytest.fixture
def inputs(user_pk):
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
def user2_sk():
    return USER2_SK


@pytest.fixture
def user2_pk():
    return USER2_PK


@pytest.fixture
def inputs_shared(user_pk, user2_pk):
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
