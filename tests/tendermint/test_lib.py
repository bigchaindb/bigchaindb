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


pytestmark = pytest.mark.tendermint


@pytest.mark.bdb
def test_asset_is_separated_from_transaciton(b):
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

    b.store_transaction(tx)
    assert 'asset' not in backend.query.get_transaction(b.connection, tx.id)
    assert backend.query.get_asset(b.connection, tx.id)['data'] == asset
    assert b.get_transaction(tx.id) == tx


@pytest.mark.bdb
def test_get_latest_block(tb):
    from bigchaindb.tendermint.lib import Block

    b = tb
    for i in range(10):
        app_hash = os.urandom(16).hex()
        txn_id = os.urandom(16).hex()
        block = Block(app_hash=app_hash, height=i,
                      transactions=[txn_id])._asdict()
        b.store_block(block)

    block = b.get_latest_block()
    assert block['height'] == 9


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
    from bigchaindb.tendermint.utils import encode_transaction

    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None)\
                    .sign([alice.private_key]).to_dict()

    tx = b.validate_transaction(tx)
    b.write_transaction(tx, 'broadcast_tx_async')

    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert 'broadcast_tx_async' == kwargs['json']['method']
    encoded_tx = [encode_transaction(tx.to_dict())]
    assert encoded_tx == kwargs['json']['params']


@patch('requests.post')
@pytest.mark.parametrize('mode', [
    'broadcast_tx_async',
    'broadcast_tx_sync',
    'broadcast_tx_commit'
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
def test_validator_updates(b, validator_pub_key):
    from bigchaindb.backend import query
    from bigchaindb.backend.query import VALIDATOR_UPDATE_ID

    # create a validator update object
    validator = {'pub_key': {'type': 'ed25519',
                             'data': validator_pub_key},
                 'power': 10}
    validator_update = {'validator': validator,
                        'update_id': VALIDATOR_UPDATE_ID}
    query.store_validator_update(b.connection, validator_update)

    updates = b.get_validator_update()
    assert updates == [validator_update['validator']]

    b.delete_validator_update()
    assert b.get_validator_update() == []


@pytest.mark.bdb
def test_update_utxoset(tb, signed_create_tx, signed_transfer_tx, db_context):
    mongo_client = MongoClient(host=db_context.host, port=db_context.port)
    tb.update_utxoset(signed_create_tx)
    utxoset = mongo_client[db_context.name]['utxos']
    assert utxoset.count() == 1
    utxo = utxoset.find_one()
    assert utxo['transaction_id'] == signed_create_tx.id
    assert utxo['output_index'] == 0
    tb.update_utxoset(signed_transfer_tx)
    assert utxoset.count() == 1
    utxo = utxoset.find_one()
    assert utxo['transaction_id'] == signed_transfer_tx.id
    assert utxo['output_index'] == 0


@pytest.mark.bdb
def test_store_transaction(mocker, tb, signed_create_tx,
                           signed_transfer_tx, db_context):
    mocked_store_asset = mocker.patch('bigchaindb.backend.query.store_asset')
    mocked_store_metadata = mocker.patch(
        'bigchaindb.backend.query.store_metadatas')
    mocked_store_transaction = mocker.patch(
        'bigchaindb.backend.query.store_transaction')
    tb.store_transaction(signed_create_tx)
    # mongo_client = MongoClient(host=db_context.host, port=db_context.port)
    # utxoset = mongo_client[db_context.name]['utxos']
    # assert utxoset.count() == 1
    # utxo = utxoset.find_one()
    # assert utxo['transaction_id'] == signed_create_tx.id
    # assert utxo['output_index'] == 0
    mocked_store_asset.assert_called_once_with(
        tb.connection,
        {'id': signed_create_tx.id, 'data': signed_create_tx.asset['data']},
    )
    mocked_store_metadata.assert_called_once_with(
        tb.connection,
        [{'id': signed_create_tx.id, 'metadata': signed_create_tx.metadata}],
    )
    mocked_store_transaction.assert_called_once_with(
        tb.connection,
        {k: v for k, v in signed_create_tx.to_dict().items()
         if k not in ('asset', 'metadata')},
    )
    mocked_store_asset.reset_mock()
    mocked_store_metadata.reset_mock()
    mocked_store_transaction.reset_mock()
    tb.store_transaction(signed_transfer_tx)
    # assert utxoset.count() == 1
    # utxo = utxoset.find_one()
    # assert utxo['transaction_id'] == signed_transfer_tx.id
    # assert utxo['output_index'] == 0
    assert not mocked_store_asset.called
    mocked_store_metadata.asser_called_once_with(
        tb.connection,
        {'id': signed_transfer_tx.id, 'metadata': signed_transfer_tx.metadata},
    )
    mocked_store_transaction.assert_called_once_with(
        tb.connection,
        {k: v for k, v in signed_transfer_tx.to_dict().items()
         if k != 'metadata'},
    )


@pytest.mark.bdb
def test_store_bulk_transaction(mocker, tb, signed_create_tx,
                                signed_transfer_tx, db_context):
    mocked_store_assets = mocker.patch(
        'bigchaindb.backend.query.store_assets')
    mocked_store_metadata = mocker.patch(
        'bigchaindb.backend.query.store_metadatas')
    mocked_store_transactions = mocker.patch(
        'bigchaindb.backend.query.store_transactions')
    tb.store_bulk_transactions((signed_create_tx,))
    # mongo_client = MongoClient(host=db_context.host, port=db_context.port)
    # utxoset = mongo_client[db_context.name]['utxos']
    # assert utxoset.count() == 1
    # utxo = utxoset.find_one()
    # assert utxo['transaction_id'] == signed_create_tx.id
    # assert utxo['output_index'] == 0
    mocked_store_assets.assert_called_once_with(
        tb.connection,
        [{'id': signed_create_tx.id, 'data': signed_create_tx.asset['data']}],
    )
    mocked_store_metadata.assert_called_once_with(
        tb.connection,
        [{'id': signed_create_tx.id, 'metadata': signed_create_tx.metadata}],
    )
    mocked_store_transactions.assert_called_once_with(
        tb.connection,
        [{k: v for k, v in signed_create_tx.to_dict().items()
         if k not in ('asset', 'metadata')}],
    )
    mocked_store_assets.reset_mock()
    mocked_store_metadata.reset_mock()
    mocked_store_transactions.reset_mock()
    tb.store_bulk_transactions((signed_transfer_tx,))
    # assert utxoset.count() == 1
    # utxo = utxoset.find_one()
    # assert utxo['transaction_id'] == signed_transfer_tx.id
    # assert utxo['output_index'] == 0
    assert not mocked_store_assets.called
    mocked_store_metadata.asser_called_once_with(
        tb.connection,
        [{'id': signed_transfer_tx.id,
          'metadata': signed_transfer_tx.metadata}],
    )
    mocked_store_transactions.assert_called_once_with(
        tb.connection,
        [{k: v for k, v in signed_transfer_tx.to_dict().items()
          if k != 'metadata'}],
    )


@pytest.mark.bdb
def test_delete_zero_unspent_outputs(b, utxoset):
    unspent_outputs, utxo_collection = utxoset
    delete_res = b.delete_unspent_outputs()
    assert delete_res is None
    assert utxo_collection.count() == 3
    assert utxo_collection.find(
        {'$or': [
            {'transaction_id': 'a', 'output_index': 0},
            {'transaction_id': 'b', 'output_index': 0},
            {'transaction_id': 'a', 'output_index': 1},
        ]}
    ).count() == 3


@pytest.mark.bdb
def test_delete_one_unspent_outputs(b, utxoset):
    unspent_outputs, utxo_collection = utxoset
    delete_res = b.delete_unspent_outputs(unspent_outputs[0])
    assert delete_res['n'] == 1
    assert utxo_collection.find(
        {'$or': [
            {'transaction_id': 'a', 'output_index': 1},
            {'transaction_id': 'b', 'output_index': 0},
        ]}
    ).count() == 2
    assert utxo_collection.find(
            {'transaction_id': 'a', 'output_index': 0}).count() == 0


@pytest.mark.bdb
def test_delete_many_unspent_outputs(b, utxoset):
    unspent_outputs, utxo_collection = utxoset
    delete_res = b.delete_unspent_outputs(*unspent_outputs[::2])
    assert delete_res['n'] == 2
    assert utxo_collection.find(
        {'$or': [
            {'transaction_id': 'a', 'output_index': 0},
            {'transaction_id': 'b', 'output_index': 0},
        ]}
    ).count() == 0
    assert utxo_collection.find(
            {'transaction_id': 'a', 'output_index': 1}).count() == 1


@pytest.mark.bdb
def test_store_zero_unspent_output(b, utxo_collection):
    res = b.store_unspent_outputs()
    assert res is None
    assert utxo_collection.count() == 0


@pytest.mark.bdb
def test_store_one_unspent_output(b, unspent_output_1, utxo_collection):
    res = b.store_unspent_outputs(unspent_output_1)
    assert res.acknowledged
    assert len(res.inserted_ids) == 1
    assert utxo_collection.find(
        {'transaction_id': unspent_output_1['transaction_id'],
         'output_index': unspent_output_1['output_index']}
    ).count() == 1


@pytest.mark.bdb
def test_store_many_unspent_outputs(b, unspent_outputs, utxo_collection):
    res = b.store_unspent_outputs(*unspent_outputs)
    assert res.acknowledged
    assert len(res.inserted_ids) == 3
    assert utxo_collection.find(
        {'transaction_id': unspent_outputs[0]['transaction_id']}
    ).count() == 3


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

    b.store_bulk_transactions([tx])

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
