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
from bigchaindb.common import crypto

USER2_SK, USER2_VK = crypto.generate_key_pair()

@pytest.fixture(autouse=True)
def restore_config(request, node_config):
    from bigchaindb import config_utils
    config_utils.set_config(node_config)


@pytest.fixture(scope='module', autouse=True)
def setup_database(request, node_config):
    print('Initializing test db')
    db_name = node_config['database']['name']
    get_conn().repl()
    try:
        r.db_create(db_name).run()
    except r.ReqlOpFailedError as e:
        if e.message == 'Database `{}` already exists.'.format(db_name):
            r.db_drop(db_name).run()
            r.db_create(db_name).run()
        else:
            raise

    print('Finished initializing test db')

    # setup tables
    r.db(db_name).table_create('bigchain').run()
    r.db(db_name).table_create('backlog').run()
    r.db(db_name).table_create('votes').run()

    # create the secondary indexes
    # to order blocks by timestamp
    r.db(db_name).table('bigchain').index_create('block_timestamp', r.row['block']['timestamp']).run()
    # to order blocks by block number
    r.db(db_name).table('bigchain').index_create('block_number', r.row['block']['block_number']).run()
    # to order transactions by timestamp
    r.db(db_name).table('backlog').index_create('transaction_timestamp', r.row['transaction']['timestamp']).run()
    # to query by payload uuid
    r.db(db_name).table('bigchain').index_create(
        'metadata_id',
        r.row['block']['transactions']['transaction']['metadata']['id'],
        multi=True,
    ).run()
    # compound index to read transactions from the backlog per assignee
    r.db(db_name).table('backlog')\
        .index_create('assignee__transaction_timestamp', [r.row['assignee'], r.row['transaction']['timestamp']])\
        .run()
    # compound index to order votes by block id and node
    r.db(db_name).table('votes').index_create('block_and_voter',
                                              [r.row['vote']['voting_for_block'], r.row['node_pubkey']]).run()
    # secondary index for asset uuid
    r.db(db_name).table('bigchain')\
                .index_create('asset_id',
                              r.row['block']['transactions']['transaction']['asset']['id'], multi=True)\
                .run()
    # order transactions by id
    r.db(db_name).table('bigchain').index_create('transaction_id', r.row['block']['transactions']['id'],
                                                 multi=True).run()

    r.db(db_name).table('bigchain').index_wait('transaction_id').run()

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
