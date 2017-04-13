""" Schema validation related functions and data """
import os.path

import jsonschema
import yaml

from bigchaindb.common.exceptions import SchemaValidationError


def drop_schema_descriptions(node):
    """ Drop descriptions from schema, since they clutter log output """
    if 'description' in node:
        del node['description']
    for n in node.get('properties', {}).values():
        drop_schema_descriptions(n)
    for n in node.get('definitions', {}).values():
        drop_schema_descriptions(n)
    for n in node.get('anyOf', []):
        drop_schema_descriptions(n)


def _load_schema(name):
    """ Load a schema from disk """
    path = os.path.join(os.path.dirname(__file__), name + '.yaml')
    with open(path) as handle:
        schema = yaml.safe_load(handle)
    drop_schema_descriptions(schema)
    return path, schema


TX_SCHEMA_PATH, TX_SCHEMA_COMMON = _load_schema('transaction')
_, TX_SCHEMA_CREATE = _load_schema('transaction_create')
_, TX_SCHEMA_TRANSFER = _load_schema('transaction_transfer')
VOTE_SCHEMA_PATH, VOTE_SCHEMA = _load_schema('vote')


def _validate_schema(schema, body):
    """ Validate data against a schema """
    try:
        jsonschema.validate(body, schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(str(exc)) from exc


def validate_transaction_schema(tx):
    """
    Validate a transaction dict.

    TX_SCHEMA_COMMON contains properties that are common to all types of
    transaction. TX_SCHEMA_[TRANSFER|CREATE] add additional constraints on top.
    """
    _validate_schema(TX_SCHEMA_COMMON, tx)
    if tx['operation'] == 'TRANSFER':
        _validate_schema(TX_SCHEMA_TRANSFER, tx)
    else:
        _validate_schema(TX_SCHEMA_CREATE, tx)


def validate_vote_schema(vote):
    """ Validate a vote dict """
    _validate_schema(VOTE_SCHEMA, vote)
