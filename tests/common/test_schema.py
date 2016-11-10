import json

import jsonschema


def test_validate_transaction_basic(create_tx):
    tx_dict = create_tx.to_dict()
    tx_schema = json.load(open('bigchaindb/common/schema/transaction.json'))
    jsonschema.validate(tx_dict, tx_schema)


def test_addition_properties_false():
    """
    Validate that each node has additionalProperties set.
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

    tx_schema = json.load(open('bigchaindb/common/schema/transaction.json'))
    walk(tx_schema)
