"""
All tests of transaction structure. The concern here is that transaction
structural / schematic issues are caught when reading a transaction
(ie going from dict -> transaction).
"""

import pytest

from bigchaindb.common.exceptions import (AmountError, InvalidHash,
                                          SchemaValidationError)
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


################################################################################
# Outputs


def test_low_amounts(create_tx, signed_transfer_tx):
    for tx in [create_tx, signed_transfer_tx]:
        tx.outputs[0].amount = 0
        validate_raises(tx, AmountError)
        tx.outputs[0].amount = -1
        validate_raises(tx, AmountError)


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
# Version

def test_validate_version(create_tx):
    import re
    import bigchaindb.version

    short_ver = bigchaindb.version.__short_version__
    assert create_tx.version == re.match(r'^(.*\d)', short_ver).group(1)

    validate(create_tx)

    # At version 1, transaction version will break step with server version.
    create_tx.version = '1.0.0'
    validate_raises(create_tx)
