import pytest


@pytest.fixture
def config(request, monkeypatch):
    config = {
        'database': {
            'host': 'host',
            'port': 28015,
            'name': 'bigchain',
        },
        'keypair': {
            'public': 'pubkey',
            'private': 'privkey',
        },
        'keyring': [],
        'CONFIGURED': True,
        'consensus_plugin': 'default'
    }

    monkeypatch.setattr('bigchaindb.config', config)

    return config


def test_bigchain_class_default_initialization(config):
    from bigchaindb.core import Bigchain
    from bigchaindb.consensus import BaseConsensusRules
    bigchain = Bigchain()
    assert bigchain.host == config['database']['host']
    assert bigchain.port == config['database']['port']
    assert bigchain.dbname == config['database']['name']
    assert bigchain.me == config['keypair']['public']
    assert bigchain.me_private == config['keypair']['private']
    assert bigchain.federation_nodes == config['keyring']
    assert bigchain.consensus == BaseConsensusRules
    assert bigchain._conn is None


def test_bigchain_class_initialization_with_parameters(config):
    from bigchaindb.core import Bigchain
    from bigchaindb.consensus import BaseConsensusRules
    init_kwargs = {
        'host': 'some_node',
        'port': '12345',
        'dbname': 'atom',
        'public_key': 'white',
        'private_key': 'black',
        'keyring': ['key_one', 'key_two'],
        'consensus_plugin': 'default'
    }
    bigchain = Bigchain(**init_kwargs)
    assert bigchain.host == init_kwargs['host']
    assert bigchain.port == init_kwargs['port']
    assert bigchain.dbname == init_kwargs['dbname']
    assert bigchain.me == init_kwargs['public_key']
    assert bigchain.me_private == init_kwargs['private_key']
    assert bigchain.federation_nodes == init_kwargs['keyring']
    assert bigchain.consensus == BaseConsensusRules
    assert bigchain._conn is None
