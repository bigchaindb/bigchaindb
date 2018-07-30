"""Schema validation related functions and data"""
import os.path
import logging

import jsonschema
import yaml
import rapidjson
import rapidjson_schema

from bigchaindb.common.exceptions import SchemaValidationError


logger = logging.getLogger(__name__)


def _load_schema(name, path=__file__):
    """Load a schema from disk"""
    path = os.path.join(os.path.dirname(path), name + '.yaml')
    with open(path) as handle:
        schema = yaml.safe_load(handle)
    fast_schema = rapidjson_schema.loads(rapidjson.dumps(schema))
    return path, (schema, fast_schema)


TX_SCHEMA_VERSION = 'v2.0'

TX_SCHEMA_PATH, TX_SCHEMA_COMMON = _load_schema('transaction_' +
                                                TX_SCHEMA_VERSION)
_, TX_SCHEMA_CREATE = _load_schema('transaction_create_' +
                                   TX_SCHEMA_VERSION)
_, TX_SCHEMA_TRANSFER = _load_schema('transaction_transfer_' +
                                     TX_SCHEMA_VERSION)

_, TX_SCHEMA_VALIDATOR_ELECTION = _load_schema('transaction_validator_election_' +
                                               TX_SCHEMA_VERSION)


def _validate_schema(schema, body):
    """Validate data against a schema"""

    # Note
    #
    # Schema validation is currently the major CPU bottleneck of
    # BigchainDB. the `jsonschema` library validates python data structures
    # directly and produces nice error messages, but validation takes 4+ ms
    # per transaction which is pretty slow. The rapidjson library validates
    # much faster at 1.5ms, however it produces _very_ poor error messages.
    # For this reason we use both, rapidjson as an optimistic pathway and
    # jsonschema as a fallback in case there is a failure, so we can produce
    # a helpful error message.

    try:
        schema[1].validate(rapidjson.dumps(body))
    except ValueError as exc:
        try:
            jsonschema.validate(body, schema[0])
        except jsonschema.ValidationError as exc2:
            raise SchemaValidationError(str(exc2)) from exc2
        logger.warning('code problem: jsonschema did not raise an exception, wheras rapidjson raised %s', exc)
        raise SchemaValidationError(str(exc)) from exc


def validate_transaction_schema(tx):
    """Validate a transaction dict.

    TX_SCHEMA_COMMON contains properties that are common to all types of
    transaction. TX_SCHEMA_[TRANSFER|CREATE] add additional constraints on top.
    """
    _validate_schema(TX_SCHEMA_COMMON, tx)
    if tx['operation'] == 'TRANSFER':
        _validate_schema(TX_SCHEMA_TRANSFER, tx)
    else:
        _validate_schema(TX_SCHEMA_CREATE, tx)
