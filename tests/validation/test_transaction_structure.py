"""
All tests of transaction structure. The concern here is that transaction
structural / schematic issues are caught when reading a transaction
(ie going from dict -> transaction).
"""

import pytest

from bigchaindb.common.exceptions import SchemaValidationError
from bigchaindb.models import Transaction


################################################################################
# Helper functions

def validate(tx):
    if isinstance(tx, Transaction):
        tx = tx.to_dict()
    Transaction.from_dict(tx)


def validate_throws(tx):
    with pytest.raises(SchemaValidationError):
        validate(tx)


################################################################################
# Metadata

def test_validate_fails_metadata_empty_dict(create_tx):
    create_tx.metadata = {'a': 1}
    validate(create_tx)
    create_tx.metadata = None
    validate(create_tx)
    create_tx.metadata = {}
    validate_throws(create_tx)


################################################################################
# Asset

def test_transfer_asset_schema(signed_transfer_tx):
    tx = signed_transfer_tx.to_dict()
    validate_transaction_schema(tx)
    tx['asset']['data'] = {}
    with raises(SchemaValidationError):
        validate_transaction_schema(tx)
    del tx['asset']['data']
    tx['asset']['id'] = 'b' * 63
    with raises(SchemaValidationError):
        validate_transaction_schema(tx)


################################################################################
# Inputs

def test_create_single_input(create_tx):
    tx = create_tx.to_dict()
    tx['inputs'] += tx['inputs']
    with raises(SchemaValidationError):
        validate_transaction_schema(tx)
    tx['inputs'] = []
    with raises(SchemaValidationError):
        validate_transaction_schema(tx)


def test_create_tx_no_fulfills(create_tx):
    tx = create_tx.to_dict()
    tx['inputs'][0]['fulfills'] = {'tx': 'a' * 64, 'output': 0}
    with raises(SchemaValidationError):
        validate_transaction_schema(tx)
