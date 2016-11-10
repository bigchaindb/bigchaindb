import jsonschema
import unittest

from bigchaindb.common import schema


class TestSchemaA(schema.SchemaObject):
    a = 'a'


class TestSchemaB(schema.SchemaObject):
    b = 'b'
    a = TestSchemaA
    _definitions = {'d': 'd'}
    _required = ['b']


def test_1(self):
    expected = {
        'properties': {
            'a': {
                'properties': {
                    'a': 'a'
                },
                'type': 'object',
            },
            'b': 'b',
        },
        'definitions': {
            'd': 'd'
        },
        'required': ['b'],
        'type': 'object',
    }
    assert TestSchemaB.to_json_schema() == expected


def test_validate_transaction_basic(create_tx):
    assert jsonschema.validate(create_tx.to_dict(),
                               schema.Transaction.to_json_schema())

