"""
All tests of transaction structure. The concern here is that transaction
structural / schematic issues are caught when reading a transaction
(ie going from dict -> transaction).
"""

import pytest
import re

from bigchaindb.common.exceptions import SchemaValidationError
from bigchaindb.models import Transaction


################################################################################
# Helper functions

def validate(tx):
    if isinstance(tx, Transaction):
        tx = tx.to_dict()
    Transaction.from_dict(tx)


def validate_raises(tx):
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


################################################################################
# Inputs

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
