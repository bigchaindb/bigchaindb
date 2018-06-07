import pytest


@pytest.fixture
def config(request, monkeypatch):
    backend = request.config.getoption('--database-backend')
    if backend == 'mongodb-ssl':
        backend = 'mongodb'

    config = {
        'database': {
            'backend': backend,
            'host': 'host',
            'port': 28015,
            'name': 'bigchain',
            'replicaset': 'bigchain-rs',
            'connection_timeout': 5000,
            'max_tries': 3
        },
        'keypair': {
            'public': 'pubkey',
            'private': 'privkey',
        },
        'keyring': [],
        'CONFIGURED': True,
    }

    monkeypatch.setattr('bigchaindb.config', config)

    return config


def test_bigchain_class_default_initialization(config):
    from bigchaindb.core import Bigchain
    from bigchaindb.consensus import BaseConsensusRules
    from bigchaindb.backend.connection import Connection
    bigchain = Bigchain()
    assert isinstance(bigchain.connection, Connection)
    assert bigchain.connection.host == config['database']['host']
    assert bigchain.connection.port == config['database']['port']
    assert bigchain.connection.dbname == config['database']['name']
    assert bigchain.me == config['keypair']['public']
    assert bigchain.me_private == config['keypair']['private']
    assert bigchain.nodes_except_me == config['keyring']
    assert bigchain.consensus == BaseConsensusRules


def test_bigchain_class_initialization_with_parameters(config):
    from bigchaindb.core import Bigchain
    from bigchaindb.backend import connect
    from bigchaindb.consensus import BaseConsensusRules
    init_kwargs = {
        'public_key': 'white',
        'private_key': 'black',
        'keyring': ['key_one', 'key_two'],
    }
    init_db_kwargs = {
        'backend': 'rethinkdb',
        'host': 'this_is_the_db_host',
        'port': 12345,
        'name': 'this_is_the_db_name',
    }
    connection = connect(**init_db_kwargs)
    bigchain = Bigchain(connection=connection, **init_kwargs)
    assert bigchain.connection == connection
    assert bigchain.connection.host == init_db_kwargs['host']
    assert bigchain.connection.port == init_db_kwargs['port']
    assert bigchain.connection.dbname == init_db_kwargs['name']
    assert bigchain.me == init_kwargs['public_key']
    assert bigchain.me_private == init_kwargs['private_key']
    assert bigchain.nodes_except_me == init_kwargs['keyring']
    assert bigchain.consensus == BaseConsensusRules


def test_get_blocks_status_containing_tx(monkeypatch):
    from bigchaindb.backend import query as backend_query
    from bigchaindb.core import Bigchain
    blocks = [
        {'id': 1}, {'id': 2}
    ]
    monkeypatch.setattr(backend_query, 'get_blocks_status_from_transaction', lambda x: blocks)
    monkeypatch.setattr(Bigchain, 'block_election_status', lambda x, y, z: Bigchain.BLOCK_VALID)
    bigchain = Bigchain(public_key='pubkey', private_key='privkey')
    with pytest.raises(Exception):
        bigchain.get_blocks_status_containing_tx('txid')


@pytest.mark.genesis
def test_get_spent_issue_1271(b, alice, bob, carol):
    from bigchaindb.models import Transaction

    tx_1 = Transaction.create(
        [carol.public_key],
        [([carol.public_key], 8)],
    ).sign([carol.private_key])

    tx_2 = Transaction.transfer(
        tx_1.to_inputs(),
        [([bob.public_key], 2),
         ([alice.public_key], 2),
         ([carol.public_key], 4)],
        asset_id=tx_1.id,
    ).sign([carol.private_key])

    tx_3 = Transaction.transfer(
        tx_2.to_inputs()[2:3],
        [([alice.public_key], 1),
         ([carol.public_key], 3)],
        asset_id=tx_1.id,
    ).sign([carol.private_key])

    tx_4 = Transaction.transfer(
        tx_2.to_inputs()[1:2] + tx_3.to_inputs()[0:1],
        [([bob.public_key], 3)],
        asset_id=tx_1.id,
    ).sign([alice.private_key])

    tx_5 = Transaction.transfer(
        tx_2.to_inputs()[0:1],
        [([alice.public_key], 2)],
        asset_id=tx_1.id,
    ).sign([bob.private_key])
    block_5 = b.create_block([tx_1, tx_2, tx_3, tx_4, tx_5])
    b.write_block(block_5)
    assert b.get_spent(tx_2.id, 0) == tx_5
    assert not b.get_spent(tx_5.id, 0)
    assert b.get_outputs_filtered(alice.public_key)
    assert b.get_outputs_filtered(alice.public_key, spent=False)
