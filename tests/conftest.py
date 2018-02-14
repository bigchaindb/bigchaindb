"""Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""

import os
import copy
import random
from collections import namedtuple

import pytest

from logging import getLogger
from logging.config import dictConfig
from bigchaindb.common import crypto

TEST_DB_NAME = 'bigchain_test'

USER2_SK, USER2_PK = crypto.generate_key_pair()

# Test user. inputs will be created for this user. Cryptography Keys
USER_PRIVATE_KEY = '8eJ8q9ZQpReWyQT5aFCiwtZ5wDZC4eDnCen88p3tQ6ie'
USER_PUBLIC_KEY = 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE'


def pytest_runtest_setup(item):
    if isinstance(item, item.Function):
        backend = item.session.config.getoption('--database-backend')
        if (item.get_marker('localmongodb') and backend != 'localmongodb'):
            pytest.skip('Skip tendermint specific tests if not using localmongodb')


def pytest_addoption(parser):
    from bigchaindb.backend.connection import BACKENDS

    BACKENDS['mongodb-ssl'] = 'bigchaindb.backend.mongodb.connection.MongoDBConnection'
    backends = ', '.join(BACKENDS.keys())
    parser.addoption(
        '--database-backend',
        action='store',
        default=os.environ.get('BIGCHAINDB_DATABASE_BACKEND', 'rethinkdb'),
        help='Defines the backend to use (available: {})'.format(backends),
    )


def pytest_ignore_collect(path, config):
    from bigchaindb.backend.connection import BACKENDS
    path = str(path)

    BACKENDS['mongodb-ssl'] = 'bigchaindb.backend.mongodb.connection.MongoDBConnection'
    supported_backends = BACKENDS.keys()

    if os.path.isdir(path):
        dirname = os.path.split(path)[1]
        if dirname in supported_backends and dirname != config.getoption('--database-backend'):
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
def _configure_bigchaindb(request, ssl_context):
    import bigchaindb
    from bigchaindb import config_utils
    test_db_name = TEST_DB_NAME
    # Put a suffix like _gw0, _gw1 etc on xdist processes
    xdist_suffix = getattr(request.config, 'slaveinput', {}).get('slaveid')
    if xdist_suffix:
        test_db_name = '{}_{}'.format(TEST_DB_NAME, xdist_suffix)

    backend = request.config.getoption('--database-backend')

    if backend == 'mongodb-ssl':
        bigchaindb._database_map[backend] = {
            # we use mongodb as the backend for mongodb-ssl
            'backend': 'mongodb',
            'connection_timeout': 5000,
            'max_tries': 3,
            'ssl': True,
            'ca_cert': ssl_context.ca,
            'crlfile': ssl_context.crl,
            'certfile': ssl_context.cert,
            'keyfile': ssl_context.key,
            'keyfile_passphrase': os.environ.get('BIGCHAINDB_DATABASE_KEYFILE_PASSPHRASE', None)
        }
        bigchaindb._database_map[backend].update(bigchaindb._base_database_mongodb)

    config = {
        'database': bigchaindb._database_map[backend],
        'keypair': {
            'private': '31Lb1ZGKTyHnmVK3LUMrAUrPNfd4sE2YyBt3UA4A25aA',
            'public': '4XYfCbabAWVUCbjTmRTFEu2sc3dFEdkse4r6X498B1s8',
        }
    }
    config['database']['name'] = test_db_name
    config_utils.set_config(config)


@pytest.fixture(scope='session')
def _setup_database(_configure_bigchaindb):
    from bigchaindb import config
    from bigchaindb.backend import connect, schema
    from bigchaindb.common.exceptions import DatabaseDoesNotExist
    print('Initializing test db')
    dbname = config['database']['name']
    conn = connect()

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
        return {}

    monkeypatch.setattr('bigchaindb.config_utils.file_config',
                        mock_file_config)


@pytest.fixture
def reset_logging_config():
    # root_logger_level = getLogger().level
    root_logger_level = 'DEBUG'
    dictConfig({'version': 1, 'root': {'level': 'NOTSET'}})
    yield
    getLogger().setLevel(root_logger_level)


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
def alice():
    from bigchaindb.common.crypto import generate_key_pair
    return generate_key_pair()


@pytest.fixture
def alice_privkey(alice):
    return alice.private_key


@pytest.fixture
def alice_pubkey(alice):
    return alice.public_key


@pytest.fixture
def bob():
    from bigchaindb.common.crypto import generate_key_pair
    return generate_key_pair()


@pytest.fixture
def bob_privkey(bob):
    return bob.private_key


@pytest.fixture
def bob_pubkey(carol):
    return bob.public_key


@pytest.fixture
def carol():
    from bigchaindb.common.crypto import generate_key_pair
    return generate_key_pair()


@pytest.fixture
def carol_privkey(carol):
    return carol.private_key


@pytest.fixture
def carol_pubkey(carol):
    return carol.public_key


@pytest.fixture
def b():
    from bigchaindb import Bigchain
    return Bigchain()


@pytest.fixture
def tb():
    from bigchaindb.tendermint import BigchainDB
    return BigchainDB()


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
def double_spend_tx(signed_create_tx, carol_pubkey, user_sk):
    from bigchaindb.models import Transaction
    inputs = signed_create_tx.to_inputs()
    tx = Transaction.transfer(
        inputs, [([carol_pubkey], 1)], asset_id=signed_create_tx.id)
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


@pytest.fixture
def db_context(db_config, db_host, db_port, db_name, db_conn):
    DBContext = namedtuple(
        'DBContext', ('config', 'host', 'port', 'name', 'conn'))
    return DBContext(
        config=db_config,
        host=db_host,
        port=db_port,
        name=db_name,
        conn=db_conn,
    )


@pytest.fixture
def tendermint_host():
    return os.getenv('BIGCHAINDB_TENDERMINT_HOST', 'localhost')


@pytest.fixture
def tendermint_port():
    return int(os.getenv('BIGCHAINDB_TENDERMINT_PORT', 46657))


@pytest.fixture
def tendermint_ws_url(tendermint_host, tendermint_port):
    return f'ws://{tendermint_host}:{tendermint_port}/websocket'


@pytest.fixture
def tendermint_context(tendermint_host, tendermint_port, tendermint_ws_url):
    TendermintContext = namedtuple(
        'TendermintContext', ('host', 'port', 'ws_url'))
    return TendermintContext(
        host=tendermint_host,
        port=tendermint_port,
        ws_url=tendermint_ws_url,
    )


@pytest.fixture
def mocked_setup_pub_logger(mocker):
    return mocker.patch(
        'bigchaindb.log.setup.setup_pub_logger', autospec=True, spec_set=True)


@pytest.fixture
def mocked_setup_sub_logger(mocker):
    return mocker.patch(
        'bigchaindb.log.setup.setup_sub_logger', autospec=True, spec_set=True)


@pytest.fixture(scope='session')
def certs_dir():
    return os.path.abspath('tests/backend/mongodb-ssl/certs')


@pytest.fixture(scope='session')
def ca_chain_cert(certs_dir):
    return os.environ.get(
        'BIGCHAINDB_DATABASE_CA_CERT',
        os.path.join(certs_dir, 'ca-chain.cert.pem'))


@pytest.fixture(scope='session')
def ssl_crl(certs_dir):
    return os.environ.get(
        'BIGCHAINDB_DATABASE_CRLFILE',
        os.path.join(certs_dir, 'crl.pem'))


@pytest.fixture(scope='session')
def ssl_cert(certs_dir):
    return os.environ.get(
        'BIGCHAINDB_DATABASE_CERTFILE',
        os.path.join(certs_dir, 'bigchaindb.cert.pem'))


@pytest.fixture(scope='session')
def ssl_key(certs_dir):
    return os.environ.get(
        'BIGCHAINDB_DATABASE_KEYFILE',
        os.path.join(certs_dir, 'bigchaindb.key.pem'))


@pytest.fixture
def mdb_ssl_pem_key(certs_dir):
    return os.environ.get(
        'BIGCHAINDB_MDB_PEM_KEY_TEST',
        os.path.join(certs_dir, 'local-mongo.pem'))


@pytest.fixture(scope='session')
def ssl_context(ca_chain_cert, ssl_crl, ssl_cert, ssl_key):
    SSLContext = namedtuple('SSLContext', ('ca', 'crl', 'cert', 'key'))
    return SSLContext(
        ca=ca_chain_cert, crl=ssl_crl, cert=ssl_cert, key=ssl_key)


@pytest.fixture
def wsserver_config():
    from bigchaindb import config
    return config['wsserver']


@pytest.fixture
def wsserver_scheme(wsserver_config):
    return wsserver_config['advertised_scheme']


@pytest.fixture
def wsserver_host(wsserver_config):
    return wsserver_config['advertised_host']


@pytest.fixture
def wsserver_port(wsserver_config):
    return wsserver_config['advertised_port']


@pytest.fixture
def wsserver_base_url(wsserver_scheme, wsserver_host, wsserver_port):
    return '{}://{}:{}'.format(wsserver_scheme, wsserver_host, wsserver_port)


@pytest.fixture
def genesis_tx(b, user_pk):
    from bigchaindb.models import Transaction
    tx = Transaction.create([b.me], [([user_pk], 1)])
    tx.operation = Transaction.GENESIS
    genesis_tx = tx.sign([b.me_private])
    return genesis_tx


@pytest.fixture
def unspent_output_0():
    return {
        'amount': 1,
        'asset_id': 'e897c7a0426461a02b4fca8ed73bc0debed7570cf3b40fb4f49c963434225a4d',
        'condition_uri': 'ni:///sha-256;RmovleG60-7K0CX60jjfUunV3lBpUOkiQOAnBzghm0w?fpt=ed25519-sha-256&cost=131072',
        'fulfillment_message': '{"asset":{"data":{"hash":"06e47bcf9084f7ecfd2a2a2ad275444a"}},"id":"e897c7a0426461a02b4fca8ed73bc0debed7570cf3b40fb4f49c963434225a4d","inputs":[{"fulfillment":"pGSAIIQT0Jm6LDlcSs9coJK4Q4W-SNtsO2EtMtQJ04EUjBMJgUAXKIqeaippbF-IClhhZNNaP6EIZ_OgrVQYU4mH6b-Vc3Tg-k6p-rJOlLGUUo_w8C5QgPHNRYFOqUk2f1q0Cs4G","fulfills":null,"owners_before":["9taLkHkaBXeSF8vrhDGFTAmcZuCEPqjQrKadfYGs4gHv"]}],"metadata":null,"operation":"CREATE","outputs":[{"amount":"1","condition":{"details":{"public_key":"6FDGsHrR9RZqNaEm7kBvqtxRkrvuWogBW2Uy7BkWc5Tz","type":"ed25519-sha-256"},"uri":"ni:///sha-256;RmovleG60-7K0CX60jjfUunV3lBpUOkiQOAnBzghm0w?fpt=ed25519-sha-256&cost=131072"},"public_keys":["6FDGsHrR9RZqNaEm7kBvqtxRkrvuWogBW2Uy7BkWc5Tz"]},{"amount":"2","condition":{"details":{"public_key":"AH9D7xgmhyLmVE944zvHvuvYWuj5DfbMBJhnDM4A5FdT","type":"ed25519-sha-256"},"uri":"ni:///sha-256;-HlYmgwwl-vXwE52IaADhvYxaL1TbjqfJ-LGn5a1PFc?fpt=ed25519-sha-256&cost=131072"},"public_keys":["AH9D7xgmhyLmVE944zvHvuvYWuj5DfbMBJhnDM4A5FdT"]},{"amount":"3","condition":{"details":{"public_key":"HpmSVrojHvfCXQbmoAs4v6Aq1oZiZsZDnjr68KiVtPbB","type":"ed25519-sha-256"},"uri":"ni:///sha-256;xfn8pvQkTCPtvR0trpHy2pqkkNTmMBCjWMMOHtk3WO4?fpt=ed25519-sha-256&cost=131072"},"public_keys":["HpmSVrojHvfCXQbmoAs4v6Aq1oZiZsZDnjr68KiVtPbB"]}],"version":"1.0"}',   # noqa
        'output_index': 0,
        'transaction_id': 'e897c7a0426461a02b4fca8ed73bc0debed7570cf3b40fb4f49c963434225a4d'
    }


@pytest.fixture
def unspent_output_1():
    return {
        'amount': 2,
        'asset_id': 'e897c7a0426461a02b4fca8ed73bc0debed7570cf3b40fb4f49c963434225a4d',
        'condition_uri': 'ni:///sha-256;-HlYmgwwl-vXwE52IaADhvYxaL1TbjqfJ-LGn5a1PFc?fpt=ed25519-sha-256&cost=131072',
        'fulfillment_message': '{"asset":{"data":{"hash":"06e47bcf9084f7ecfd2a2a2ad275444a"}},"id":"e897c7a0426461a02b4fca8ed73bc0debed7570cf3b40fb4f49c963434225a4d","inputs":[{"fulfillment":"pGSAIIQT0Jm6LDlcSs9coJK4Q4W-SNtsO2EtMtQJ04EUjBMJgUAXKIqeaippbF-IClhhZNNaP6EIZ_OgrVQYU4mH6b-Vc3Tg-k6p-rJOlLGUUo_w8C5QgPHNRYFOqUk2f1q0Cs4G","fulfills":null,"owners_before":["9taLkHkaBXeSF8vrhDGFTAmcZuCEPqjQrKadfYGs4gHv"]}],"metadata":null,"operation":"CREATE","outputs":[{"amount":"1","condition":{"details":{"public_key":"6FDGsHrR9RZqNaEm7kBvqtxRkrvuWogBW2Uy7BkWc5Tz","type":"ed25519-sha-256"},"uri":"ni:///sha-256;RmovleG60-7K0CX60jjfUunV3lBpUOkiQOAnBzghm0w?fpt=ed25519-sha-256&cost=131072"},"public_keys":["6FDGsHrR9RZqNaEm7kBvqtxRkrvuWogBW2Uy7BkWc5Tz"]},{"amount":"2","condition":{"details":{"public_key":"AH9D7xgmhyLmVE944zvHvuvYWuj5DfbMBJhnDM4A5FdT","type":"ed25519-sha-256"},"uri":"ni:///sha-256;-HlYmgwwl-vXwE52IaADhvYxaL1TbjqfJ-LGn5a1PFc?fpt=ed25519-sha-256&cost=131072"},"public_keys":["AH9D7xgmhyLmVE944zvHvuvYWuj5DfbMBJhnDM4A5FdT"]},{"amount":"3","condition":{"details":{"public_key":"HpmSVrojHvfCXQbmoAs4v6Aq1oZiZsZDnjr68KiVtPbB","type":"ed25519-sha-256"},"uri":"ni:///sha-256;xfn8pvQkTCPtvR0trpHy2pqkkNTmMBCjWMMOHtk3WO4?fpt=ed25519-sha-256&cost=131072"},"public_keys":["HpmSVrojHvfCXQbmoAs4v6Aq1oZiZsZDnjr68KiVtPbB"]}],"version":"1.0"}',   # noqa
        'output_index': 1,
        'transaction_id': 'e897c7a0426461a02b4fca8ed73bc0debed7570cf3b40fb4f49c963434225a4d',
    }


@pytest.fixture
def unspent_output_2():
    return {
        'amount': 3,
        'asset_id': 'e897c7a0426461a02b4fca8ed73bc0debed7570cf3b40fb4f49c963434225a4d',
        'condition_uri': 'ni:///sha-256;xfn8pvQkTCPtvR0trpHy2pqkkNTmMBCjWMMOHtk3WO4?fpt=ed25519-sha-256&cost=131072',
        'fulfillment_message': '{"asset":{"data":{"hash":"06e47bcf9084f7ecfd2a2a2ad275444a"}},"id":"e897c7a0426461a02b4fca8ed73bc0debed7570cf3b40fb4f49c963434225a4d","inputs":[{"fulfillment":"pGSAIIQT0Jm6LDlcSs9coJK4Q4W-SNtsO2EtMtQJ04EUjBMJgUAXKIqeaippbF-IClhhZNNaP6EIZ_OgrVQYU4mH6b-Vc3Tg-k6p-rJOlLGUUo_w8C5QgPHNRYFOqUk2f1q0Cs4G","fulfills":null,"owners_before":["9taLkHkaBXeSF8vrhDGFTAmcZuCEPqjQrKadfYGs4gHv"]}],"metadata":null,"operation":"CREATE","outputs":[{"amount":"1","condition":{"details":{"public_key":"6FDGsHrR9RZqNaEm7kBvqtxRkrvuWogBW2Uy7BkWc5Tz","type":"ed25519-sha-256"},"uri":"ni:///sha-256;RmovleG60-7K0CX60jjfUunV3lBpUOkiQOAnBzghm0w?fpt=ed25519-sha-256&cost=131072"},"public_keys":["6FDGsHrR9RZqNaEm7kBvqtxRkrvuWogBW2Uy7BkWc5Tz"]},{"amount":"2","condition":{"details":{"public_key":"AH9D7xgmhyLmVE944zvHvuvYWuj5DfbMBJhnDM4A5FdT","type":"ed25519-sha-256"},"uri":"ni:///sha-256;-HlYmgwwl-vXwE52IaADhvYxaL1TbjqfJ-LGn5a1PFc?fpt=ed25519-sha-256&cost=131072"},"public_keys":["AH9D7xgmhyLmVE944zvHvuvYWuj5DfbMBJhnDM4A5FdT"]},{"amount":"3","condition":{"details":{"public_key":"HpmSVrojHvfCXQbmoAs4v6Aq1oZiZsZDnjr68KiVtPbB","type":"ed25519-sha-256"},"uri":"ni:///sha-256;xfn8pvQkTCPtvR0trpHy2pqkkNTmMBCjWMMOHtk3WO4?fpt=ed25519-sha-256&cost=131072"},"public_keys":["HpmSVrojHvfCXQbmoAs4v6Aq1oZiZsZDnjr68KiVtPbB"]}],"version":"1.0"}',   # noqa
        'output_index': 2,
        'transaction_id': 'e897c7a0426461a02b4fca8ed73bc0debed7570cf3b40fb4f49c963434225a4d',
    }


@pytest.fixture
def unspent_outputs(unspent_output_0, unspent_output_1, unspent_output_2):
    return unspent_output_0, unspent_output_1, unspent_output_2
