# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import os
from unittest.mock import patch


try:
    from hashlib import sha3_256
except ImportError:
    # NOTE: neeeded for Python < 3.6
    from sha3 import sha3_256

import pytest
from pymongo import MongoClient

from bigchaindb import backend
from bigchaindb.common.transaction_mode_types import (BROADCAST_TX_COMMIT,
                                                      BROADCAST_TX_ASYNC,
                                                      BROADCAST_TX_SYNC)
from bigchaindb.lib import Block


@pytest.mark.bdb
def test_asset_is_separated_from_transaciton(b):
    import copy
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    asset = {'Never gonna': ['give you up',
                             'let you down',
                             'run around'
                             'desert you',
                             'make you cry',
                             'say goodbye',
                             'tell a lie',
                             'hurt you']}

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)],
                            metadata=None,
                            asset=asset)\
                    .sign([alice.private_key])

    # with store_bulk_transactions we use `insert_many` where PyMongo
    # automatically adds an `_id` field to the tx, therefore we need the
    # deepcopy, for more info see:
    # https://api.mongodb.com/python/current/faq.html#writes-and-ids
    tx_dict = copy.deepcopy(tx.to_dict())

    b.store_bulk_transactions([tx])
    assert 'asset' not in backend.query.get_transaction(b.connection, tx.id)
    assert backend.query.get_asset(b.connection, tx.id)['data'] == asset
    assert b.get_transaction(tx.id).to_dict() == tx_dict


@pytest.mark.bdb
def test_get_latest_block(b):
    from bigchaindb.lib import Block

    for i in range(10):
        app_hash = os.urandom(16).hex()
        txn_id = os.urandom(16).hex()
        block = Block(app_hash=app_hash, height=i,
                      transactions=[txn_id])._asdict()
        b.store_block(block)

    block = b.get_latest_block()
    assert block['height'] == 9


@pytest.mark.bdb
@patch('bigchaindb.backend.query.get_block', return_value=None)
@patch('bigchaindb.BigchainDB.get_latest_block', return_value={'height': 10})
def test_get_empty_block(_0, _1, b):
    assert b.get_block(5) == {'height': 5, 'transactions': []}


def test_validation_error(b):
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None)\
                    .sign([alice.private_key]).to_dict()

    tx['metadata'] = ''
    assert not b.validate_transaction(tx)


@patch('requests.post')
def test_write_and_post_transaction(mock_post, b):
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.tendermint_utils import encode_transaction

    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None)\
                    .sign([alice.private_key]).to_dict()

    tx = b.validate_transaction(tx)
    b.write_transaction(tx, BROADCAST_TX_ASYNC)

    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert BROADCAST_TX_ASYNC == kwargs['json']['method']
    encoded_tx = [encode_transaction(tx.to_dict())]
    assert encoded_tx == kwargs['json']['params']


@patch('requests.post')
@pytest.mark.parametrize('mode', [
    BROADCAST_TX_SYNC,
    BROADCAST_TX_ASYNC,
    BROADCAST_TX_COMMIT
])
def test_post_transaction_valid_modes(mock_post, b, mode):
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair
    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None) \
        .sign([alice.private_key]).to_dict()
    tx = b.validate_transaction(tx)
    b.write_transaction(tx, mode)

    args, kwargs = mock_post.call_args
    assert mode == kwargs['json']['method']


def test_post_transaction_invalid_mode(b):
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.common.exceptions import ValidationError
    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None) \
        .sign([alice.private_key]).to_dict()
    tx = b.validate_transaction(tx)
    with pytest.raises(ValidationError):
        b.write_transaction(tx, 'nope')


@pytest.mark.bdb
def test_update_utxoset(b, signed_create_tx, signed_transfer_tx, db_context):
    mongo_client = MongoClient(host=db_context.host, port=db_context.port)
    b.update_utxoset(signed_create_tx)
    utxoset = mongo_client[db_context.name]['utxos']
    assert utxoset.count_documents({}) == 1
    utxo = utxoset.find_one()
    assert utxo['transaction_id'] == signed_create_tx.id
    assert utxo['output_index'] == 0
    b.update_utxoset(signed_transfer_tx)
    assert utxoset.count_documents({}) == 1
    utxo = utxoset.find_one()
    assert utxo['transaction_id'] == signed_transfer_tx.id
    assert utxo['output_index'] == 0


@pytest.mark.bdb
def test_store_transaction(mocker, b, signed_create_tx,
                           signed_transfer_tx, db_context):
    mocked_store_asset = mocker.patch('bigchaindb.backend.query.store_assets')
    mocked_store_metadata = mocker.patch(
        'bigchaindb.backend.query.store_metadatas')
    mocked_store_transaction = mocker.patch(
        'bigchaindb.backend.query.store_transactions')
    b.store_bulk_transactions([signed_create_tx])
    # mongo_client = MongoClient(host=db_context.host, port=db_context.port)
    # utxoset = mongo_client[db_context.name]['utxos']
    # assert utxoset.count_documents({}) == 1
    # utxo = utxoset.find_one()
    # assert utxo['transaction_id'] == signed_create_tx.id
    # assert utxo['output_index'] == 0

    mocked_store_asset.assert_called_once_with(
        b.connection,
        [{'id': signed_create_tx.id, 'data': signed_create_tx.asset['data']}],
    )
    mocked_store_metadata.assert_called_once_with(
        b.connection,
        [{'id': signed_create_tx.id, 'metadata': signed_create_tx.metadata}],
    )
    mocked_store_transaction.assert_called_once_with(
        b.connection,
        [{k: v for k, v in signed_create_tx.to_dict().items()
         if k not in ('asset', 'metadata')}],
    )
    mocked_store_asset.reset_mock()
    mocked_store_metadata.reset_mock()
    mocked_store_transaction.reset_mock()
    b.store_bulk_transactions([signed_transfer_tx])
    # assert utxoset.count_documents({}) == 1
    # utxo = utxoset.find_one()
    # assert utxo['transaction_id'] == signed_transfer_tx.id
    # assert utxo['output_index'] == 0
    assert not mocked_store_asset.called
    mocked_store_metadata.asser_called_once_with(
        b.connection,
        [{'id': signed_transfer_tx.id, 'metadata': signed_transfer_tx.metadata}],
    )
    mocked_store_transaction.assert_called_once_with(
        b.connection,
        [{k: v for k, v in signed_transfer_tx.to_dict().items()
         if k != 'metadata'}],
    )


@pytest.mark.bdb
def test_store_bulk_transaction(mocker, b, signed_create_tx,
                                signed_transfer_tx, db_context):
    mocked_store_assets = mocker.patch(
        'bigchaindb.backend.query.store_assets')
    mocked_store_metadata = mocker.patch(
        'bigchaindb.backend.query.store_metadatas')
    mocked_store_transactions = mocker.patch(
        'bigchaindb.backend.query.store_transactions')
    b.store_bulk_transactions((signed_create_tx,))
    # mongo_client = MongoClient(host=db_context.host, port=db_context.port)
    # utxoset = mongo_client[db_context.name]['utxos']
    # assert utxoset.count_documents({}) == 1
    # utxo = utxoset.find_one()
    # assert utxo['transaction_id'] == signed_create_tx.id
    # assert utxo['output_index'] == 0
    mocked_store_assets.assert_called_once_with(
        b.connection,
        [{'id': signed_create_tx.id, 'data': signed_create_tx.asset['data']}],
    )
    mocked_store_metadata.assert_called_once_with(
        b.connection,
        [{'id': signed_create_tx.id, 'metadata': signed_create_tx.metadata}],
    )
    mocked_store_transactions.assert_called_once_with(
        b.connection,
        [{k: v for k, v in signed_create_tx.to_dict().items()
         if k not in ('asset', 'metadata')}],
    )
    mocked_store_assets.reset_mock()
    mocked_store_metadata.reset_mock()
    mocked_store_transactions.reset_mock()
    b.store_bulk_transactions((signed_transfer_tx,))
    # assert utxoset.count_documents({}) == 1
    # utxo = utxoset.find_one()
    # assert utxo['transaction_id'] == signed_transfer_tx.id
    # assert utxo['output_index'] == 0
    assert not mocked_store_assets.called
    mocked_store_metadata.asser_called_once_with(
        b.connection,
        [{'id': signed_transfer_tx.id,
          'metadata': signed_transfer_tx.metadata}],
    )
    mocked_store_transactions.assert_called_once_with(
        b.connection,
        [{k: v for k, v in signed_transfer_tx.to_dict().items()
          if k != 'metadata'}],
    )


@pytest.mark.bdb
def test_delete_zero_unspent_outputs(b, utxoset):
    unspent_outputs, utxo_collection = utxoset
    delete_res = b.delete_unspent_outputs()
    assert delete_res is None
    assert utxo_collection.count_documents({}) == 3
    assert utxo_collection.count_documents(
        {'$or': [
            {'transaction_id': 'a', 'output_index': 0},
            {'transaction_id': 'b', 'output_index': 0},
            {'transaction_id': 'a', 'output_index': 1},
        ]}
    ) == 3


@pytest.mark.bdb
def test_delete_one_unspent_outputs(b, utxoset):
    unspent_outputs, utxo_collection = utxoset
    delete_res = b.delete_unspent_outputs(unspent_outputs[0])
    assert delete_res.raw_result['n'] == 1
    assert utxo_collection.count_documents(
        {'$or': [
            {'transaction_id': 'a', 'output_index': 1},
            {'transaction_id': 'b', 'output_index': 0},
        ]}
    ) == 2
    assert utxo_collection.count_documents(
            {'transaction_id': 'a', 'output_index': 0}) == 0


@pytest.mark.bdb
def test_delete_many_unspent_outputs(b, utxoset):
    unspent_outputs, utxo_collection = utxoset
    delete_res = b.delete_unspent_outputs(*unspent_outputs[::2])
    assert delete_res.raw_result['n'] == 2
    assert utxo_collection.count_documents(
        {'$or': [
            {'transaction_id': 'a', 'output_index': 0},
            {'transaction_id': 'b', 'output_index': 0},
        ]}
    ) == 0
    assert utxo_collection.count_documents(
            {'transaction_id': 'a', 'output_index': 1}) == 1


@pytest.mark.bdb
def test_store_zero_unspent_output(b, utxo_collection):
    res = b.store_unspent_outputs()
    assert res is None
    assert utxo_collection.count_documents({}) == 0


@pytest.mark.bdb
def test_store_one_unspent_output(b, unspent_output_1, utxo_collection):
    res = b.store_unspent_outputs(unspent_output_1)
    assert res.acknowledged
    assert len(res.inserted_ids) == 1
    assert utxo_collection.count_documents(
        {'transaction_id': unspent_output_1['transaction_id'],
         'output_index': unspent_output_1['output_index']}
    ) == 1


@pytest.mark.bdb
def test_store_many_unspent_outputs(b, unspent_outputs, utxo_collection):
    res = b.store_unspent_outputs(*unspent_outputs)
    assert res.acknowledged
    assert len(res.inserted_ids) == 3
    assert utxo_collection.count_documents(
        {'transaction_id': unspent_outputs[0]['transaction_id']}
    ) == 3


def test_get_utxoset_merkle_root_when_no_utxo(b):
    assert b.get_utxoset_merkle_root() == sha3_256(b'').hexdigest()


@pytest.mark.bdb
@pytest.mark.usefixture('utxoset')
def test_get_utxoset_merkle_root(b, utxoset):
    expected_merkle_root = (
        '86d311c03115bf4d287f8449ca5828505432d69b82762d47077b1c00fe426eac')
    merkle_root = b.get_utxoset_merkle_root()
    assert merkle_root == expected_merkle_root


@pytest.mark.bdb
def test_get_spent_transaction_critical_double_spend(b, alice, bob, carol):
    from bigchaindb.models import Transaction
    from bigchaindb.exceptions import CriticalDoubleSpend
    from bigchaindb.common.exceptions import DoubleSpend

    asset = {'test': 'asset'}

    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=asset)\
                    .sign([alice.private_key])

    tx_transfer = Transaction.transfer(tx.to_inputs(),
                                       [([bob.public_key], 1)],
                                       asset_id=tx.id)\
                             .sign([alice.private_key])

    double_spend = Transaction.transfer(tx.to_inputs(),
                                        [([carol.public_key], 1)],
                                        asset_id=tx.id)\
                              .sign([alice.private_key])

    same_input_double_spend = Transaction.transfer(tx.to_inputs() + tx.to_inputs(),
                                                   [([bob.public_key], 1)],
                                                   asset_id=tx.id)\
                                         .sign([alice.private_key])

    b.store_bulk_transactions([tx])

    with pytest.raises(DoubleSpend):
        same_input_double_spend.validate(b)

    assert b.get_spent(tx.id, tx_transfer.inputs[0].fulfills.output, [tx_transfer])

    with pytest.raises(DoubleSpend):
        b.get_spent(tx.id, tx_transfer.inputs[0].fulfills.output,
                    [tx_transfer, double_spend])

    b.store_bulk_transactions([tx_transfer])

    with pytest.raises(DoubleSpend):
        b.get_spent(tx.id, tx_transfer.inputs[0].fulfills.output, [double_spend])

    b.store_bulk_transactions([double_spend])

    with pytest.raises(CriticalDoubleSpend):
        b.get_spent(tx.id, tx_transfer.inputs[0].fulfills.output)


def test_validation_with_transaction_buffer(b):
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.models import Transaction

    priv_key, pub_key = generate_key_pair()

    create_tx = Transaction.create([pub_key], [([pub_key], 10)]).sign([priv_key])
    transfer_tx = Transaction.transfer(create_tx.to_inputs(),
                                       [([pub_key], 10)],
                                       asset_id=create_tx.id).sign([priv_key])
    double_spend = Transaction.transfer(create_tx.to_inputs(),
                                        [([pub_key], 10)],
                                        asset_id=create_tx.id).sign([priv_key])

    assert b.is_valid_transaction(create_tx)
    assert b.is_valid_transaction(transfer_tx, [create_tx])

    assert not b.is_valid_transaction(create_tx, [create_tx])
    assert not b.is_valid_transaction(transfer_tx, [create_tx, transfer_tx])
    assert not b.is_valid_transaction(double_spend, [create_tx, transfer_tx])


@pytest.mark.bdb
def test_migrate_abci_chain_yields_on_genesis(b):
    b.migrate_abci_chain()
    latest_chain = b.get_latest_abci_chain()
    assert latest_chain is None


@pytest.mark.bdb
@pytest.mark.parametrize('chain,block_height,expected', [
    (
        (1, 'chain-XYZ', True),
        4,
        {'height': 5, 'chain_id': 'chain-XYZ-migrated-at-height-4',
         'is_synced': False},
    ),
    (
        (5, 'chain-XYZ-migrated-at-height-4', True),
        13,
        {'height': 14, 'chain_id': 'chain-XYZ-migrated-at-height-13',
         'is_synced': False},
    ),
])
def test_migrate_abci_chain_generates_new_chains(b, chain, block_height,
                                                 expected):
    b.store_abci_chain(*chain)
    b.store_block(Block(app_hash='', height=block_height,
                        transactions=[])._asdict())
    b.migrate_abci_chain()
    latest_chain = b.get_latest_abci_chain()
    assert latest_chain == expected


@pytest.mark.bdb
def test_get_spent_key_order(b, user_pk, user_sk, user2_pk, user2_sk):
    from bigchaindb import backend
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.common.exceptions import DoubleSpend

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx1 = Transaction.create([user_pk],
                             [([alice.public_key], 3), ([user_pk], 2)],
                             asset=None)\
                     .sign([user_sk])
    b.store_bulk_transactions([tx1])

    inputs = tx1.to_inputs()
    tx2 = Transaction.transfer([inputs[1]], [([user2_pk], 2)], tx1.id).sign([user_sk])
    assert tx2.validate(b)

    tx2_dict = tx2.to_dict()
    fulfills = tx2_dict['inputs'][0]['fulfills']
    tx2_dict['inputs'][0]['fulfills'] = {'output_index': fulfills['output_index'],
                                         'transaction_id': fulfills['transaction_id']}

    backend.query.store_transactions(b.connection, [tx2_dict])

    tx3 = Transaction.transfer([inputs[1]], [([bob.public_key], 2)], tx1.id).sign([user_sk])

    with pytest.raises(DoubleSpend):
        tx3.validate(b)
