# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

"""Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""
import json
import os
import copy
import random
import tempfile
from collections import namedtuple
from logging import getLogger
from logging.config import dictConfig

import pytest
from pymongo import MongoClient

from bigchaindb import ValidatorElection
from bigchaindb.common import crypto
from bigchaindb.common.transaction_mode_types import BROADCAST_TX_COMMIT
from bigchaindb.tendermint_utils import key_from_base64
from bigchaindb.backend import schema, query
from bigchaindb.common.crypto import (key_pair_from_ed25519_key,
                                      public_key_from_ed25519_key)
from bigchaindb.common.exceptions import DatabaseDoesNotExist
from bigchaindb.lib import Block
from tests.utils import gen_vote

TEST_DB_NAME = 'bigchain_test'

USER2_SK, USER2_PK = crypto.generate_key_pair()

# Test user. inputs will be created for this user. Cryptography Keys
USER_PRIVATE_KEY = '8eJ8q9ZQpReWyQT5aFCiwtZ5wDZC4eDnCen88p3tQ6ie'
USER_PUBLIC_KEY = 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE'


def pytest_addoption(parser):
    from bigchaindb.backend.connection import BACKENDS

    backends = ', '.join(BACKENDS.keys())
    parser.addoption(
        '--database-backend',
        action='store',
        default=os.environ.get('BIGCHAINDB_DATABASE_BACKEND', 'localmongodb'),
        help='Defines the backend to use (available: {})'.format(backends),
    )


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


@pytest.fixture(scope='session')
def _setup_database(_configure_bigchaindb):
    from bigchaindb import config
    from bigchaindb.backend import connect
    print('Initializing test db')
    dbname = config['database']['name']
    conn = connect()

    _drop_db(conn, dbname)
    schema.init_database(conn)
    print('Finishing init database')

    yield

    print('Deleting `{}` database'.format(dbname))
    conn = connect()
    _drop_db(conn, dbname)

    print('Finished deleting `{}`'.format(dbname))


@pytest.fixture
def _bdb(_setup_database, _configure_bigchaindb):
    from bigchaindb import config
    from bigchaindb.backend import connect
    from .utils import flush_db
    from bigchaindb.common.memoize import to_dict, from_dict
    from bigchaindb.models import Transaction
    conn = connect()
    yield
    dbname = config['database']['name']
    flush_db(conn, dbname)

    to_dict.cache_clear()
    from_dict.cache_clear()
    Transaction._input_valid.cache_clear()


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
def b():
    from bigchaindb import BigchainDB
    return BigchainDB()


@pytest.fixture
def b_mock(b, network_validators):
    b.get_validators = mock_get_validators(network_validators)

    return b


def mock_get_validators(network_validators):
    def validator_set(height):
        validators = []
        for public_key, power in network_validators.items():
            validators.append({
                'public_key': {'type': 'ed25519-base64', 'value': public_key},
                'voting_power': power
            })
        return validators

    return validator_set


@pytest.fixture
def create_tx(alice, user_pk):
    from bigchaindb.models import Transaction
    name = f'I am created by the create_tx fixture. My random identifier is {random.random()}.'
    return Transaction.create([alice.public_key], [([user_pk], 1)], asset={'name': name})


@pytest.fixture
def signed_create_tx(alice, create_tx):
    return create_tx.sign([alice.private_key])


@pytest.fixture
def posted_create_tx(b, signed_create_tx):
    res = b.post_transaction(signed_create_tx, BROADCAST_TX_COMMIT)
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
    for height in range(1, 4):
        transactions = [
            Transaction.create(
                [alice.public_key],
                [([user_pk], 1)],
                metadata={'msg': random.random()},
            ).sign([alice.private_key])
            for _ in range(10)
        ]
        tx_ids = [tx.id for tx in transactions]
        block = Block(app_hash='hash'+str(height), height=height, transactions=tx_ids)
        b.store_block(block._asdict())
        b.store_bulk_transactions(transactions)


@pytest.fixture
def dummy_db(request):
    from bigchaindb.backend import connect

    conn = connect()
    dbname = request.fixturename
    xdist_suffix = getattr(request.config, 'slaveinput', {}).get('slaveid')
    if xdist_suffix:
        dbname = '{}_{}'.format(dbname, xdist_suffix)

    _drop_db(conn, dbname)  # make sure we start with a clean DB
    schema.init_database(conn, dbname)
    yield dbname

    _drop_db(conn, dbname)


def _drop_db(conn, dbname):
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

        except requests.exceptions.RequestException:
            pass
        time.sleep(1)

    return False


@pytest.yield_fixture(scope='session')
def event_loop():
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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


@pytest.fixture
def network_validators(node_keys):
    validator_pub_power = {}
    voting_power = [8, 10, 7, 9]
    for pub, priv in node_keys.items():
        validator_pub_power[pub] = voting_power.pop()

    return validator_pub_power


@pytest.fixture
def network_validators58(network_validators):
    network_validators_base58 = {}
    for p, v in network_validators.items():
        p = public_key_from_ed25519_key(key_from_base64(p))
        network_validators_base58[p] = v

    return network_validators_base58


@pytest.fixture
def node_key(node_keys):
    (pub, priv) = list(node_keys.items())[0]
    return key_pair_from_ed25519_key(key_from_base64(priv))


@pytest.fixture
def ed25519_node_keys(node_keys):
    (pub, priv) = list(node_keys.items())[0]
    node_keys_dict = {}
    for pub, priv in node_keys.items():
        key = key_pair_from_ed25519_key(key_from_base64(priv))
        node_keys_dict[key.public_key] = key

    return node_keys_dict


@pytest.fixture
def node_keys():
    return {'zL/DasvKulXZzhSNFwx4cLRXKkSM9GPK7Y0nZ4FEylM=':
            'cM5oW4J0zmUSZ/+QRoRlincvgCwR0pEjFoY//ZnnjD3Mv8Nqy8q6VdnOFI0XDHhwtFcqRIz0Y8rtjSdngUTKUw==',
            'GIijU7GBcVyiVUcB0GwWZbxCxdk2xV6pxdvL24s/AqM=':
            'mdz7IjP6mGXs6+ebgGJkn7kTXByUeeGhV+9aVthLuEAYiKNTsYFxXKJVRwHQbBZlvELF2TbFXqnF28vbiz8Cow==',
            'JbfwrLvCVIwOPm8tj8936ki7IYbmGHjPiKb6nAZegRA=':
            '83VINXdj2ynOHuhvSZz5tGuOE5oYzIi0mEximkX1KYMlt/Csu8JUjA4+by2Pz3fqSLshhuYYeM+IpvqcBl6BEA==',
            'PecJ58SaNRsWJZodDmqjpCWqG6btdwXFHLyE40RYlYM=':
            'uz8bYgoL4rHErWT1gjjrnA+W7bgD/uDQWSRKDmC8otc95wnnxJo1GxYlmh0OaqOkJaobpu13BcUcvITjRFiVgw=='}


@pytest.fixture
def priv_validator_path(node_keys):
    (public_key, private_key) = list(node_keys.items())[0]
    priv_validator = {
        'address': '84F787D95E196DC5DE5F972666CFECCA36801426',
        'pub_key': {
            'type': 'AC26791624DE60',
            'value': public_key
        },
        'last_height': 0,
        'last_round': 0,
        'last_step': 0,
        'priv_key': {
            'type': '954568A3288910',
            'value': private_key
        }
    }
    fd, path = tempfile.mkstemp()
    socket = os.fdopen(fd, 'w')
    json.dump(priv_validator, socket)
    socket.close()
    return path


@pytest.fixture
def bad_validator_path(node_keys):
    (public_key, private_key) = list(node_keys.items())[1]
    priv_validator = {
        'address': '84F787D95E196DC5DE5F972666CFECCA36801426',
        'pub_key': {
            'type': 'AC26791624DE60',
            'value': public_key
        },
        'last_height': 0,
        'last_round': 0,
        'last_step': 0,
        'priv_key': {
            'type': '954568A3288910',
            'value': private_key
        }
    }
    fd, path = tempfile.mkstemp()
    socket = os.fdopen(fd, 'w')
    json.dump(priv_validator, socket)
    socket.close()
    return path


@pytest.fixture
def validators(b, node_keys):
    from bigchaindb.backend import query
    import time

    def timestamp():  # we need this to force unique election_ids for setup and teardown of fixtures
        return str(time.time())

    height = get_block_height(b)

    original_validators = b.get_validators()

    (public_key, private_key) = list(node_keys.items())[0]

    validator_set = [{'address': 'F5426F0980E36E03044F74DD414248D29ABCBDB2',
                      'public_key': {'value': public_key,
                                     'type': 'ed25519-base64'},
                      'voting_power': 10}]

    validator_update = {'validators': validator_set,
                        'height': height + 1,
                        'election_id': f'setup_at_{timestamp()}'}

    query.store_validator_set(b.connection, validator_update)

    yield

    height = get_block_height(b)

    validator_update = {'validators': original_validators,
                        'height': height,
                        'election_id': f'teardown_at_{timestamp()}'}

    query.store_validator_set(b.connection, validator_update)


def get_block_height(b):

    if b.get_latest_block():
        height = b.get_latest_block()['height']
    else:
        height = 0

    return height


@pytest.fixture
def new_validator():
    public_key = '1718D2DBFF00158A0852A17A01C78F4DCF3BA8E4FB7B8586807FAC182A535034'
    power = 1
    node_id = 'fake_node_id'

    return {'public_key': {'value': public_key,
                           'type': 'ed25519-base16'},
            'power': power,
            'node_id': node_id}


@pytest.fixture
def valid_upsert_validator_election(b_mock, node_key, new_validator):
    voters = ValidatorElection.recipients(b_mock)
    return ValidatorElection.generate([node_key.public_key],
                                      voters,
                                      new_validator, None).sign([node_key.private_key])


@pytest.fixture
def valid_upsert_validator_election_2(b_mock, node_key, new_validator):
    voters = ValidatorElection.recipients(b_mock)
    return ValidatorElection.generate([node_key.public_key],
                                      voters,
                                      new_validator, None).sign([node_key.private_key])


@pytest.fixture
def ongoing_validator_election(b, valid_upsert_validator_election, ed25519_node_keys):
    validators = b.get_validators(height=1)
    genesis_validators = {'validators': validators,
                          'height': 0}
    query.store_validator_set(b.connection, genesis_validators)
    b.store_bulk_transactions([valid_upsert_validator_election])
    query.store_election(b.connection, valid_upsert_validator_election.id, 1,
                         is_concluded=False)
    block_1 = Block(app_hash='hash_1', height=1,
                    transactions=[valid_upsert_validator_election.id])
    b.store_block(block_1._asdict())
    return valid_upsert_validator_election


@pytest.fixture
def ongoing_validator_election_2(b, valid_upsert_validator_election_2, ed25519_node_keys):
    validators = b.get_validators(height=1)
    genesis_validators = {'validators': validators,
                          'height': 0,
                          'election_id': None}
    query.store_validator_set(b.connection, genesis_validators)

    b.store_bulk_transactions([valid_upsert_validator_election_2])
    block_1 = Block(app_hash='hash_2', height=1, transactions=[valid_upsert_validator_election_2.id])
    b.store_block(block_1._asdict())
    return valid_upsert_validator_election_2


@pytest.fixture
def validator_election_votes(b_mock, ongoing_validator_election, ed25519_node_keys):
    voters = ValidatorElection.recipients(b_mock)
    votes = generate_votes(ongoing_validator_election, voters, ed25519_node_keys)
    return votes


@pytest.fixture
def validator_election_votes_2(b_mock, ongoing_validator_election_2, ed25519_node_keys):
    voters = ValidatorElection.recipients(b_mock)
    votes = generate_votes(ongoing_validator_election_2, voters, ed25519_node_keys)
    return votes


def generate_votes(election, voters, keys):
    votes = []
    for voter, _ in enumerate(voters):
        v = gen_vote(election, voter, keys)
        votes.append(v)
    return votes
