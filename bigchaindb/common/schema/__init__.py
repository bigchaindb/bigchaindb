""" Schema validation related functions and data """
import os.path

import jsonschema
import yaml

from bigchaindb.common.exceptions import SchemaValidationError


TX_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'transaction.yaml')
with open(TX_SCHEMA_PATH) as handle:
    TX_SCHEMA_YAML = handle.read()
TX_SCHEMA = yaml.safe_load(TX_SCHEMA_YAML)


def validate_transaction_schema(tx_body):
    """ Validate a transaction dict against a schema """
    try:
        jsonschema.validate(tx_body, TX_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(str(exc))


__all__ = ['TX_SCHEMA', 'TX_SCHEMA_YAML', 'validate_transaction_schema']
