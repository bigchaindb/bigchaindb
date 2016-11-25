from copy import deepcopy
from bigchaindb.common.schema import TX_SCHEMA, VOTE_SCHEMA, \
    drop_schema_descriptions


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
                ("additionalProperties not set at path:" + path)
        for name, val in node.items():
            _test_additionalproperties(val, path + name + '.')


def test_transaction_schema_additionalproperties():
    _test_additionalproperties(TX_SCHEMA)


def test_vote_schema_additionalproperties():
    _test_additionalproperties(VOTE_SCHEMA)


def test_drop_descriptions():
    node = {
        'a': 1,
        'description': 'abc',
        'b': [{
            'type': 'object',
            'description': 'gone, baby',
        }]
    }
    node2 = deepcopy(node)
    drop_schema_descriptions(node)
    del node2['b'][0]['description']
    assert node == node2
