from collections import namedtuple

from rethinkdb.ast import RqlQuery

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
        'consensus_plugin': 'default',
        'backlog_reassign_delay': 30
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
    assert bigchain.nodes_except_me == config['keyring']
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
    assert bigchain.nodes_except_me == init_kwargs['keyring']
    assert bigchain.consensus == BaseConsensusRules
    assert bigchain._conn is None


def test_get_blocks_status_containing_tx(monkeypatch):
    from bigchaindb.core import Bigchain
    blocks = [
        {'id': 1}, {'id': 2}
    ]
    monkeypatch.setattr(
        Bigchain, 'search_block_election_on_index', lambda x, y, z: blocks)
    monkeypatch.setattr(
        Bigchain, 'block_election_status', lambda x, y: Bigchain.BLOCK_VALID)
    bigchain = Bigchain(public_key='pubkey', private_key='privkey')
    with pytest.raises(Exception):
        bigchain.get_blocks_status_containing_tx('txid')


def test_has_previous_vote(monkeypatch):
    from bigchaindb.core import Bigchain
    monkeypatch.setattr(
        'bigchaindb.util.verify_vote_signature', lambda block, vote: False)
    bigchain = Bigchain(public_key='pubkey', private_key='privkey')
    block = {'votes': ({'node_pubkey': 'pubkey'},)}
    with pytest.raises(Exception):
        bigchain.has_previous_vote(block)


@pytest.mark.parametrize('items,exists', (((0,), True), ((), False)))
def test_transaction_exists(monkeypatch, items, exists):
    from bigchaindb.core import Bigchain
    monkeypatch.setattr(
        RqlQuery, 'run', lambda x, y: namedtuple('response', 'items')(items))
    bigchain = Bigchain(public_key='pubkey', private_key='privkey')
    assert bigchain.transaction_exists('txid') is exists


def test_write_transaction_no_sideffects(b):
    from rethinkdb.errors import ReqlOpFailedError
    transaction = {'id': 'abc'}
    expected = {'id': 'abc'}
    with pytest.raises(ReqlOpFailedError):
        b.write_transaction(transaction)
    assert transaction == expected
    with pytest.raises(KeyError):
        transaction['assignee']
