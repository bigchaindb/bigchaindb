"""
Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""

import pytest
import rethinkdb as r

from bigchaindb import Bigchain
from bigchaindb.db import get_conn, init_database
from bigchaindb.common import crypto
from bigchaindb.exceptions import DatabaseAlreadyExists

USER2_SK, USER2_VK = crypto.generate_key_pair()


@pytest.fixture(autouse=True)
def restore_config(request, node_config):
    from bigchaindb import config_utils
    config_utils.set_config(node_config)


@pytest.fixture(scope='module', autouse=True)
def setup_database(request, node_config):
    print('Initializing test db')
    db_name = node_config['database']['name']
    conn = get_conn()

    if r.db_list().contains(db_name).run(conn):
        r.db_drop(db_name).run(conn)

    try:
        init_database()
    except DatabaseAlreadyExists:
        print('Database already exists.')

    print('Finishing init database')

    def fin():
        print('Deleting `{}` database'.format(db_name))
        get_conn().repl()
        try:
            r.db_drop(db_name).run()
        except r.ReqlOpFailedError as e:
            if e.message != 'Database `{}` does not exist.'.format(db_name):
                raise
        print('Finished deleting `{}`'.format(db_name))

    request.addfinalizer(fin)


@pytest.fixture(scope='function', autouse=True)
def cleanup_tables(request, node_config):
    db_name = node_config['database']['name']

    def fin():
        get_conn().repl()
        try:
            r.db(db_name).table('bigchain').delete().run()
            r.db(db_name).table('backlog').delete().run()
            r.db(db_name).table('votes').delete().run()
        except r.ReqlOpFailedError as e:
            if e.message != 'Database `{}` does not exist.'.format(db_name):
                raise

    request.addfinalizer(fin)


@pytest.fixture
def inputs(user_vk):
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
            Transaction.create([b.me], [user_vk]).sign([b.me_private])
            for i in range(10)
        ]
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # 3. vote the blocks valid, so that the inputs are valid
        vote = b.vote(block.id, prev_block_id, True)
        prev_block_id = block.id
        b.write_vote(vote)


@pytest.fixture
def user2_sk():
    return USER2_SK


@pytest.fixture
def user2_vk():
    return USER2_VK


@pytest.fixture
def inputs_shared(user_vk, user2_vk):
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
                [b.me], [user_vk, user2_vk], payload={'i': i}).sign([b.me_private])
            for i in range(10)
        ]
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # 3. vote the blocks valid, so that the inputs are valid
        vote = b.vote(block.id, prev_block_id, True)
        prev_block_id = block.id
        b.write_vote(vote)
