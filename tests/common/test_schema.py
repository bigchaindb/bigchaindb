from bigchaindb.common.schema import SchemaObject
import unittest


class TestSchemaA(SchemaObject):
    a = 'a'


class TestSchemaB(SchemaObject):
    b = 'b'
    a = TestSchemaA
    _definitions = {'d': 'd'}


class TestSchemaObject(unittest.TestCase):
    def test_1(self):
        self.assertEqual(TestSchemaB.to_json_schema(), {
            'properties': {
                'a': {
                    'properties': {
                        'a': 'a'
                    }
                },
                'b': 'b',
            },
            'definitions': {
                'd': 'd'
            },
        })
