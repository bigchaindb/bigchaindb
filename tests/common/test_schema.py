from bigchaindb.common.schema import TX_JSON_SCHEMA

import jsonschema


def test_validate_transaction_create(create_tx):
    jsonschema.validate(create_tx.to_dict(), TX_JSON_SCHEMA)


def test_validate_transaction_signed_create(signed_create_tx):
    jsonschema.validate(signed_create_tx.to_dict(), TX_JSON_SCHEMA)


def test_validate_transaction_signed_transfer(signed_transfer_tx):
    jsonschema.validate(signed_transfer_tx.to_dict(), TX_JSON_SCHEMA)


def test_addition_properties_false():
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

    walk(TX_JSON_SCHEMA)
