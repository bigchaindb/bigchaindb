""" Schema validation related functions and data """
import os.path

import jsonschema
import yaml

from bigchaindb.common.exceptions import SchemaValidationError


def _load_schema(name):
    """ Load a schema from disk """
    path = os.path.join(os.path.dirname(__file__), name + '.yaml')
    with open(path) as handle:
        return path, yaml.safe_load(handle)


def _validate_schema(schema, body):
    """ Validate data against a schema """
    try:
        jsonschema.validate(body, schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(str(exc)) from exc


TX_SCHEMA_PATH, TX_SCHEMA = _load_schema('transaction')
VOTE_SCHEMA_PATH, VOTE_SCHEMA = _load_schema('vote')


def validate_transaction_schema(tx_body):
    """ Validate a transaction dict """
    _validate_schema(TX_SCHEMA, tx_body)


def validate_vote_schema(tx_body):
    """ Validate a vote dict """
    _validate_schema(VOTE_SCHEMA, tx_body)

