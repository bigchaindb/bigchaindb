
from bigchaindb.common.schema import SchemaObject
import unittest


class TestSchemaA(SchemaObject):
    c = 'c'


class TestSchemaB(SchemaObject):
    a = 'a'
    b = TestSchemaA


class TestSchemaObject(unittest.TestCase):
    def test_1(self):
        expected = {'properties': {'b': {'properties': {'c': 'c'}}, 'a': 'a'}}

        assert TestSchemaB.to_json_schema() == {
            'properties': {
                'b': {
                    'properties': {
                        'c': 'c'
                    }
                },
                'a': 'a'
            }
        }
