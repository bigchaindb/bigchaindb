""" Schema validation related functions and data """
from collections import OrderedDict
import os.path

import jsonschema
import yaml

from bigchaindb.common.exceptions import SchemaValidationError


def ordered_load(stream):
    """ Custom YAML loader to preserve key order """
    class OrderedLoader(yaml.SafeLoader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return OrderedDict(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


TX_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'transaction.yaml')
TX_SCHEMA_DATA = open(TX_SCHEMA_PATH).read()
TX_SCHEMA = yaml.load(TX_SCHEMA_DATA, yaml.SafeLoader)
TX_SCHEMA_ORDERED = ordered_load(TX_SCHEMA_DATA)


def validate_transaction_schema(tx_body):
    """ Validate a transaction dict against a schema """
    try:
        jsonschema.validate(tx_body, TX_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(str(exc))


__all__ = ['TX_SCHEMA', 'TX_SCHEMA_ORDERED', 'validate_transaction_schema']
