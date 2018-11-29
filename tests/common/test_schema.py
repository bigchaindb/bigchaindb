# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

"""This module is tests related to schema checking, but _not_ of granular schematic
properties related to validation.
"""

from unittest.mock import patch

from hypothesis import given
from hypothesis_regex import regex
from pytest import raises

from bigchaindb.common.exceptions import SchemaValidationError
from bigchaindb.common.schema import (
    TX_SCHEMA_COMMON,
    validate_transaction_schema,
)

SUPPORTED_CRYPTOCONDITION_TYPES = ('threshold-sha-256', 'ed25519-sha-256')
UNSUPPORTED_CRYPTOCONDITION_TYPES = (
    'preimage-sha-256', 'prefix-sha-256', 'rsa-sha-256')


################################################################################
# Test of schema utils


def _test_additionalproperties(node, path=''):
    """Validate that each object node has additionalProperties set, so that
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


def test_validate_failure_inconsistent():
    with patch('jsonschema.validate'):
        with raises(SchemaValidationError):
            validate_transaction_schema({})


@given(condition_uri=regex(
    r'^ni:\/\/\/sha-256;([a-zA-Z0-9_-]{{0,86}})\?fpt=({})'
    r'&cost=[0-9]+(?![\n])$'.format('|'.join(
        t for t in SUPPORTED_CRYPTOCONDITION_TYPES))))
def test_condition_uri_with_supported_fpt(dummy_transaction, condition_uri):
    dummy_transaction['outputs'][0]['condition']['uri'] = condition_uri
    validate_transaction_schema(dummy_transaction)


@given(condition_uri=regex(r'^ni:\/\/\/sha-256;([a-zA-Z0-9_-]{{0,86}})\?fpt='
                           r'({})&cost=[0-9]+(?![\n])$'.format(
                               '|'.join(UNSUPPORTED_CRYPTOCONDITION_TYPES))))
def test_condition_uri_with_unsupported_fpt(dummy_transaction, condition_uri):
    dummy_transaction['outputs'][0]['condition']['uri'] = condition_uri
    with raises(SchemaValidationError):
        validate_transaction_schema(dummy_transaction)


@given(condition_uri=regex(
    r'^ni:\/\/\/sha-256;([a-zA-Z0-9_-]{{0,86}})\?fpt=(?!{})'
    r'&cost=[0-9]+(?![\n])$'.format('$|'.join(
        t for t in SUPPORTED_CRYPTOCONDITION_TYPES))))
def test_condition_uri_with_unknown_fpt(dummy_transaction, condition_uri):
    dummy_transaction['outputs'][0]['condition']['uri'] = condition_uri
    with raises(SchemaValidationError):
        validate_transaction_schema(dummy_transaction)


@given(condition_uri=regex(
    r'^ni:\/\/\/sha-256;([a-zA-Z0-9_-]{0,86})\?fpt=threshold-sha-256'
    r'&cost=[0-9]+&subtypes=ed25519-sha-256(?![\n])$'))
def test_condition_uri_with_supported_subtype(dummy_transaction,
                                              condition_uri):
    dummy_transaction['outputs'][0]['condition']['uri'] = condition_uri
    validate_transaction_schema(dummy_transaction)


@given(condition_uri=regex(
    r'^ni:\/\/\/sha-256;([a-zA-Z0-9_-]{0,86})\?fpt=threshold-sha-256&cost='
    r'[0-9]+&subtypes=(preimage-sha-256|prefix-sha-256|rsa-sha-256)(?![\n])$'))
def test_condition_uri_with_unsupported_subtype(dummy_transaction,
                                                condition_uri):
    dummy_transaction['outputs'][0]['condition']['uri'] = condition_uri
    with raises(SchemaValidationError):
        validate_transaction_schema(dummy_transaction)


@given(condition_uri=regex(
    r'^ni:\/\/\/sha-256;([a-zA-Z0-9_-]{{0,86}})\?fpt=threshold-sha-256'
    r'&cost=[0-9]+&subtypes=(?!{})(?![\n])$'.format('$|'.join(
        t for t in SUPPORTED_CRYPTOCONDITION_TYPES))))
def test_condition_uri_with_unknown_subtype(dummy_transaction, condition_uri):
    dummy_transaction['outputs'][0]['condition']['uri'] = condition_uri
    with raises(SchemaValidationError):
        validate_transaction_schema(dummy_transaction)
