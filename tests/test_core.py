# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

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
        'tendermint': {
            'host': 'localhost',
            'port': 26657,
        },
        'CONFIGURED': True,
    }

    monkeypatch.setattr('bigchaindb.config', config)

    return config


def test_bigchain_class_default_initialization(config):
    from bigchaindb import BigchainDB
    from bigchaindb.validation import BaseValidationRules
    from bigchaindb.backend.connection import Connection
    bigchain = BigchainDB()
    assert isinstance(bigchain.connection, Connection)
    assert bigchain.connection.host == config['database']['host']
    assert bigchain.connection.port == config['database']['port']
    assert bigchain.connection.dbname == config['database']['name']
    assert bigchain.validation == BaseValidationRules


def test_bigchain_class_initialization_with_parameters():
    from bigchaindb import BigchainDB
    from bigchaindb.backend import connect
    from bigchaindb.validation import BaseValidationRules
    init_db_kwargs = {
        'backend': 'localmongodb',
        'host': 'this_is_the_db_host',
        'port': 12345,
        'name': 'this_is_the_db_name',
    }
    connection = connect(**init_db_kwargs)
    bigchain = BigchainDB(connection=connection)
    assert bigchain.connection == connection
    assert bigchain.connection.host == init_db_kwargs['host']
    assert bigchain.connection.port == init_db_kwargs['port']
    assert bigchain.connection.dbname == init_db_kwargs['name']
    assert bigchain.validation == BaseValidationRules


@pytest.mark.bdb
def test_get_spent_issue_1271(b, alice, bob, carol):
    from bigchaindb.models import Transaction

    tx_1 = Transaction.create(
        [carol.public_key],
        [([carol.public_key], 8)],
    ).sign([carol.private_key])
    assert tx_1.validate(b)
    b.store_bulk_transactions([tx_1])

    tx_2 = Transaction.transfer(
        tx_1.to_inputs(),
        [([bob.public_key], 2),
         ([alice.public_key], 2),
         ([carol.public_key], 4)],
        asset_id=tx_1.id,
    ).sign([carol.private_key])
    assert tx_2.validate(b)
    b.store_bulk_transactions([tx_2])

    tx_3 = Transaction.transfer(
        tx_2.to_inputs()[2:3],
        [([alice.public_key], 1),
         ([carol.public_key], 3)],
        asset_id=tx_1.id,
    ).sign([carol.private_key])
    assert tx_3.validate(b)
    b.store_bulk_transactions([tx_3])

    tx_4 = Transaction.transfer(
        tx_2.to_inputs()[1:2] + tx_3.to_inputs()[0:1],
        [([bob.public_key], 3)],
        asset_id=tx_1.id,
    ).sign([alice.private_key])
    assert tx_4.validate(b)
    b.store_bulk_transactions([tx_4])

    tx_5 = Transaction.transfer(
        tx_2.to_inputs()[0:1],
        [([alice.public_key], 2)],
        asset_id=tx_1.id,
    ).sign([bob.private_key])
    assert tx_5.validate(b)

    b.store_bulk_transactions([tx_5])

    assert b.get_spent(tx_2.id, 0) == tx_5
    assert not b.get_spent(tx_5.id, 0)
    assert b.get_outputs_filtered(alice.public_key)
    assert b.get_outputs_filtered(alice.public_key, spent=False)
