import jsonschema

from bigchaindb.common import schema


class TestSchemaA(schema.SchemaObject):
    a = 'a'


class TestSchemaB(schema.SchemaObject):
    b = 'b'
    a = TestSchemaA
    _definitions = {'d': 'd'}
    _required = ['b']


def test_1():
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
    tx_dict = create_tx.to_dict()
    tx_schema = schema.Transaction.to_json_schema()
    try:
        assert jsonschema.validate(tx_dict, tx_schema)
    except Exception as e:
        import pdb; pdb.set_trace()
        1

