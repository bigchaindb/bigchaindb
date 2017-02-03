from bigchaindb.common.schema import (
    TX_SCHEMA, VOTE_SCHEMA, drop_schema_descriptions)


def _test_additionalproperties(node, path=''):
    """
    Validate that each object node has additionalProperties set, so that
    objects with junk keys do not pass as valid.
    """
    if isinstance(node, list):
        for i, nnode in enumerate(node):
            _test_additionalproperties(nnode, path + str(i) + '.')
    if isinstance(node, dict):
        if node.get('type') == 'object':
            assert 'additionalProperties' in node, \
                ('additionalProperties not set at path:' + path)
        for name, val in node.items():
            _test_additionalproperties(val, path + name + '.')


def test_transaction_schema_additionalproperties():
    _test_additionalproperties(TX_SCHEMA)


def test_vote_schema_additionalproperties():
    _test_additionalproperties(VOTE_SCHEMA)


def test_drop_descriptions():
    node = {
        'description': 'abc',
        'properties': {
            'description': {
                'description': ('The property named "description" should stay'
                                'but description meta field goes'),
            },
            'properties': {
                'description': 'this must go'
            },
            'any': {
                'anyOf': [
                    {
                        'description': 'must go'
                    }
                ]
            }
        },
        'definitions': {
            'wat': {
                'description': 'go'
            }
        }
    }
    expected = {
        'properties': {
            'description': {},
            'properties': {},
            'any': {
                'anyOf': [
                    {}
                ]
            }
        },
        'definitions': {
            'wat': {},
        }
    }
    drop_schema_descriptions(node)
    assert node == expected
