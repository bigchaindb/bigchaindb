"""
This module is tests related to schema checking, but _not_ of granular schematic
properties related to validation.
"""

from pytest import raises

from bigchaindb.common.exceptions import SchemaValidationError
from bigchaindb.common.schema import (
    TX_SCHEMA_COMMON, VOTE_SCHEMA, drop_schema_descriptions,
    validate_transaction_schema, validate_vote_schema)


################################################################################
# Test of schema utils

def _test_additionalproperties(node, path=''):
    """
    Validate that each object node has additionalProperties set, so that
    objects with junk keys do not pass as valid.
    """
    if isinstance(node, list):
        for i, nnode in enumerate(node):
            _test_additionalproperties(nnode, path + str(i) + '.')
    if isinstance(node, dict):
        if node.get('type') == 'object':
            assert 'additionalProperties' in node, \
                ('additionalProperties not set at path:' + path)
        for name, val in node.items():
            _test_additionalproperties(val, path + name + '.')


def test_transaction_schema_additionalproperties():
    _test_additionalproperties(TX_SCHEMA_COMMON)


def test_vote_schema_additionalproperties():
    _test_additionalproperties(VOTE_SCHEMA)


def test_drop_descriptions():
    node = {
        'description': 'abc',
        'properties': {
            'description': {
                'description': ('The property named "description" should stay'
                                'but description meta field goes'),
            },
            'properties': {
                'description': 'this must go'
            },
            'any': {
                'anyOf': [
                    {
                        'description': 'must go'
                    }
                ]
            }
        },
        'definitions': {
            'wat': {
                'description': 'go'
            }
        }
    }
    expected = {
        'properties': {
            'description': {},
            'properties': {},
            'any': {
                'anyOf': [
                    {}
                ]
            }
        },
        'definitions': {
            'wat': {},
        }
    }
    drop_schema_descriptions(node)
    assert node == expected


################################################################################
# Test call transaction schema


def test_validate_transaction_create(create_tx):
    validate_transaction_schema(create_tx.to_dict())


def test_validate_transaction_signed_create(signed_create_tx):
    validate_transaction_schema(signed_create_tx.to_dict())


def test_validate_transaction_signed_transfer(signed_transfer_tx):
    validate_transaction_schema(signed_transfer_tx.to_dict())


def test_validate_transaction_fails():
    with raises(SchemaValidationError):
        validate_transaction_schema({})


################################################################################
# Test call vote schema


def test_validate_vote(structurally_valid_vote):
    validate_vote_schema(structurally_valid_vote)


def test_validate_vote_fails():
    with raises(SchemaValidationError):
        validate_vote_schema({})
