from pytest import raises

from bigchaindb.common.exceptions import SchemaValidationError
from bigchaindb.common.schema import TX_SCHEMA, validate_transaction_schema


def test_validate_transaction_create(create_tx):
    validate_transaction_schema(create_tx.to_dict())


def test_validate_transaction_signed_create(signed_create_tx):
    validate_transaction_schema(signed_create_tx.to_dict())


def test_validate_transaction_signed_transfer(signed_transfer_tx):
    validate_transaction_schema(signed_transfer_tx.to_dict())


def test_validation_fails():
    with raises(SchemaValidationError):
        validate_transaction_schema({})


def test_addition_properties_always_set():
    """
    Validate that each object node has additionalProperties set, so that
    transactions with junk keys do not pass as valid.
    """
    def walk(node, path=''):
        if isinstance(node, list):
            for i, nnode in enumerate(node):
                walk(nnode, path + str(i) + '.')
        if isinstance(node, dict):
            if node.get('type') == 'object':
                assert 'additionalProperties' in node, \
                    ("additionalProperties not set at path:" + path)
            for name, val in node.items():
                walk(val, path + name + '.')

    walk(TX_SCHEMA)
