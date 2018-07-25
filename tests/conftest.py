"""Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""

import os
import copy
import random
from collections import namedtuple
from logging import getLogger
from logging.config import dictConfig

import pytest
from pymongo import MongoClient

from bigchaindb.common import crypto
from bigchaindb.log import setup_logging
from bigchaindb.lib import Block

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

    backends = ', '.join(BACKENDS.keys())
    parser.addoption(
        '--database-backend',
        action='store',
        default=os.environ.get('BIGCHAINDB_DATABASE_BACKEND', 'localmongodb'),
        help='Defines the backend to use (available: {})'.format(backends),
    )


def pytest_ignore_collect(path, config):
    from bigchaindb.backend.connection import BACKENDS
    path = str(path)

    supported_backends = BACKENDS.keys()

    if os.path.isdir(path):
        dirname = os.path.split(path)[1]
        if dirname in supported_backends and dirname != config.getoption('--database-backend'):
            print('Ignoring unrequested backend test dir: ', path)
            return True


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'bdb(): Mark the test as needing BigchainDB.'
        'BigchainDB will be configured such that the database and tables are available for an '
        'entire test session.'
        'You need to run a backend (e.g. MongoDB) '
        'prior to running tests with this marker. You should not need to restart the backend '
        'in between tests runs since the test infrastructure flushes the backend upon session end.'
    )
    config.addinivalue_line(
        'markers',
        'abci(): Mark the test as needing a running ABCI server in place. Use this marker'
        'for tests that require a running Tendermint instance. Note that the test infrastructure'
        'has no way to reset Tendermint data upon session end - you need to do it manually.'
        'Setup performed by this marker includes the steps performed by the bdb marker.'
    )


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


@pytest.fixture(scope='session')
def _configure_bigchaindb(request):
    import bigchaindb
    from bigchaindb import config_utils
    test_db_name = TEST_DB_NAME
    # Put a suffix like _gw0, _gw1 etc on xdist processes
    xdist_suffix = getattr(request.config, 'slaveinput', {}).get('slaveid')
    if xdist_suffix:
        test_db_name = '{}_{}'.format(TEST_DB_NAME, xdist_suffix)

    backend = request.config.getoption('--database-backend')

    config = {
        'database': bigchaindb._database_map[backend],
        'tendermint': {
            'host': 'localhost',
            'port': 26657,
        }
    }
    config['database']['name'] = test_db_name
    config = config_utils.env_config(config)
    config_utils.set_config(config)

    # NOTE: since we use a custom log level
    # for benchmark logging we need to setup logging
    setup_logging()


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
    from .utils import flush_db
    conn = connect()
    yield
    dbname = config['database']['name']
    flush_db(conn, dbname)


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
def merlin():
    from bigchaindb.common.crypto import generate_key_pair
    return generate_key_pair()


@pytest.fixture
def merlin_privkey(merlin):
    return merlin.private_key


@pytest.fixture
def merlin_pubkey(merlin):
    return merlin.public_key


@pytest.fixture
def b():
    from bigchaindb import BigchainDB
    return BigchainDB()


@pytest.fixture
def tb():
    from bigchaindb import BigchainDB
    return BigchainDB()


@pytest.fixture
def create_tx(alice, user_pk):
    from bigchaindb.models import Transaction
    name = f'I am created by the create_tx fixture. My random identifier is {random.random()}.'
    return Transaction.create([alice.public_key], [([user_pk], 1)], asset={'name': name})


@pytest.fixture
def signed_create_tx(alice, create_tx):
    return create_tx.sign([alice.private_key])


@pytest.mark.abci
@pytest.fixture
def posted_create_tx(b, signed_create_tx):
    res = b.post_transaction(signed_create_tx, 'broadcast_tx_commit')
    assert res.status_code == 200
    return signed_create_tx


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


def _get_height(b):
    maybe_block = b.get_latest_block()
    return 0 if maybe_block is None else maybe_block['height']


@pytest.fixture
def inputs(user_pk, b, alice):
    from bigchaindb.models import Transaction
    # create blocks with transactions for `USER` to spend
    for block in range(4):
        transactions = [
            Transaction.create(
                [alice_pubkey(alice)],
                [([user_pk], 1)],
                metadata={'msg': random.random()},
            ).sign([alice_privkey(alice)]).to_dict()
            for _ in range(10)
        ]
        block = Block(app_hash='', height=_get_height(b), transactions=transactions)
        b.store_block(block._asdict())


@pytest.fixture
def inputs_shared(user_pk, user2_pk, alice):
    from bigchaindb.models import Transaction

    # create blocks with transactions for `USER` to spend
    for block in range(4):
        transactions = [
            Transaction.create(
                [alice.public_key],
                [user_pk, user2_pk],
                metadata={'msg': random.random()},
            ).sign([alice.private_key]).to_dict()
            for _ in range(10)
        ]
        block = Block(app_hash='', height=_get_height(b), transaction=transactions)
        b.store_block(block._asdict())


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
    return int(os.getenv('BIGCHAINDB_TENDERMINT_PORT', 26657))


@pytest.fixture
def tendermint_ws_url(tendermint_host, tendermint_port):
    return 'ws://{}:{}/websocket'.format(tendermint_host, tendermint_port)


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


@pytest.fixture(autouse=True)
def _abci_http(request):
    if request.keywords.get('abci', None):
        request.getfixturevalue('abci_http')


@pytest.fixture
def abci_http(_setup_database, _configure_bigchaindb, abci_server,
              tendermint_host, tendermint_port):
    import requests
    import time

    for i in range(300):
        try:
            uri = 'http://{}:{}/abci_info'.format(tendermint_host, tendermint_port)
            requests.get(uri)
            return True

        except requests.exceptions.RequestException as e:
            pass
        time.sleep(1)

    return False


@pytest.yield_fixture(scope='session')
def event_loop(request):
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.bdb
@pytest.fixture(scope='session')
def abci_server():
    from abci import ABCIServer
    from bigchaindb.core import App
    from bigchaindb.utils import Process

    app = ABCIServer(app=App())
    abci_proxy = Process(name='ABCI', target=app.run)
    yield abci_proxy.start()
    abci_proxy.terminate()


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


@pytest.fixture
def mongo_client(db_context):
    return MongoClient(host=db_context.host, port=db_context.port)


@pytest.fixture
def utxo_collection(db_context, mongo_client):
    return mongo_client[db_context.name].utxos


@pytest.fixture
def dummy_unspent_outputs():
    return [
        {'transaction_id': 'a', 'output_index': 0},
        {'transaction_id': 'a', 'output_index': 1},
        {'transaction_id': 'b', 'output_index': 0},
    ]


@pytest.fixture
def utxoset(dummy_unspent_outputs, utxo_collection):
    res = utxo_collection.insert_many(copy.deepcopy(dummy_unspent_outputs))
    assert res.acknowledged
    assert len(res.inserted_ids) == 3
    return dummy_unspent_outputs, utxo_collection
