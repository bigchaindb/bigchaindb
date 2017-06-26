"""
All tests of transaction structure. The concern here is that transaction
structural / schematic issues are caught when reading a transaction
(ie going from dict -> transaction).
"""

import pytest
from unittest.mock import MagicMock

from bigchaindb.common.exceptions import (AmountError, InvalidHash,
                                          SchemaValidationError,
                                          ThresholdTooDeep)
from bigchaindb.models import Transaction


################################################################################
# Helper functions


def validate(tx):
    if isinstance(tx, Transaction):
        tx = tx.to_dict()
    Transaction.from_dict(tx)


def validate_raises(tx, exc=SchemaValidationError):
    with pytest.raises(exc):
        validate(tx)


# We should test that validation works when we expect it to
def test_validation_passes(create_tx):
    validate(create_tx)


################################################################################
# ID


def test_tx_serialization_hash_function(create_tx):
    import sha3
    import json
    tx = create_tx.to_dict()
    tx['inputs'][0]['fulfillment'] = None
    del tx['id']
    payload = json.dumps(tx, skipkeys=False, sort_keys=True,
                         separators=(',', ':'))
    assert sha3.sha3_256(payload.encode()).hexdigest() == create_tx.id


def test_tx_serialization_with_incorrect_hash(create_tx):
    tx = create_tx.to_dict()
    tx['id'] = 'a' * 64
    validate_raises(tx, InvalidHash)


def test_tx_serialization_with_no_hash(create_tx):
    tx = create_tx.to_dict()
    del tx['id']
    validate_raises(tx)


################################################################################
# Operation

def test_validate_invalid_operation(create_tx):
    create_tx.operation = 'something invalid'
    validate_raises(create_tx)


################################################################################
# Metadata

def test_validate_fails_metadata_empty_dict(create_tx):
    create_tx.metadata = {'a': 1}
    validate(create_tx)
    create_tx.metadata = None
    validate(create_tx)
    create_tx.metadata = {}
    validate_raises(create_tx)


################################################################################
# Asset

def test_transfer_asset_schema(signed_transfer_tx):
    tx = signed_transfer_tx.to_dict()
    validate(tx)
    tx['asset']['data'] = {}
    validate_raises(tx)
    del tx['asset']['data']
    tx['asset']['id'] = 'b' * 63
    validate_raises(tx)


def test_create_tx_no_asset_id(create_tx):
    create_tx.asset['id'] = 'b' * 64
    validate_raises(create_tx)


def test_create_tx_asset_type(create_tx):
    create_tx.asset['data'] = 'a'
    validate_raises(create_tx)


def test_create_tx_no_asset_data(create_tx):
    tx_body = create_tx.to_dict()
    del tx_body['asset']['data']
    tx_body_no_signatures = Transaction._remove_signatures(tx_body)
    tx_body_serialized = Transaction._to_str(tx_body_no_signatures)
    tx_body['id'] = Transaction._to_hash(tx_body_serialized)
    validate_raises(tx_body)


################################################################################
# Inputs

def test_no_inputs(create_tx):
    create_tx.inputs = []
    validate_raises(create_tx)


def test_create_single_input(create_tx):
    tx = create_tx.to_dict()
    tx['inputs'] += tx['inputs']
    validate_raises(tx)
    tx['inputs'] = []
    validate_raises(tx)


def test_create_tx_no_fulfills(create_tx):
    tx = create_tx.to_dict()
    tx['inputs'][0]['fulfills'] = {'tx': 'a' * 64, 'output': 0}
    validate_raises(tx)


def test_transfer_has_inputs(signed_transfer_tx):
    signed_transfer_tx.inputs = []
    validate_raises(signed_transfer_tx)


################################################################################
# Outputs

def test_low_amounts(create_tx, signed_transfer_tx):
    for tx in [create_tx, signed_transfer_tx]:
        tx.outputs[0].amount = 0
        validate_raises(tx, AmountError)
        tx.outputs[0].amount = -1
        validate_raises(tx)


def test_high_amounts(create_tx):
    # Should raise a SchemaValidationError - don't want to allow ridiculously
    # large numbers to get converted to int
    create_tx.outputs[0].amount = 10 ** 21
    validate_raises(create_tx)
    # Should raise AmountError
    create_tx.outputs[0].amount = 9 * 10 ** 18 + 1
    validate_raises(create_tx, AmountError)
    # Should pass
    create_tx.outputs[0].amount -= 1
    validate(create_tx)


################################################################################
# Conditions

def test_handle_threshold_overflow():
    from bigchaindb.common import transaction

    cond = {
        'type': 'ed25519-sha-256',
        'public_key': 'a' * 43,
    }
    for i in range(1000):
        cond = {
            'type': 'threshold-sha-256',
            'threshold': 1,
            'subconditions': [cond],
        }
    with pytest.raises(ThresholdTooDeep):
        transaction._fulfillment_from_details(cond)


def test_unsupported_condition_type():
    from bigchaindb.common import transaction
    from cryptoconditions.exceptions import UnsupportedTypeError

    with pytest.raises(UnsupportedTypeError):
        transaction._fulfillment_from_details({'type': 'a'})

    with pytest.raises(UnsupportedTypeError):
        transaction._fulfillment_to_details(MagicMock(type_name='a'))


################################################################################
# Version

def test_validate_version(create_tx):
    create_tx.version = '1.0'
    validate(create_tx)
    create_tx.version = '0.10'
    validate_raises(create_tx)
    create_tx.version = '110'
    validate_raises(create_tx)
