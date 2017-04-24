from pytest import raises

from bigchaindb.common.exceptions import SchemaValidationError
from bigchaindb.common.schema import validate_transaction_schema


def test_validate_transaction_create(create_tx):
    validate_transaction_schema(create_tx.to_dict())


def test_validate_transaction_signed_create(signed_create_tx):
    validate_transaction_schema(signed_create_tx.to_dict())


def test_validate_transaction_signed_transfer(signed_transfer_tx):
    validate_transaction_schema(signed_transfer_tx.to_dict())


def test_validate_transaction_fails():
    with raises(SchemaValidationError):
        validate_transaction_schema({})


def test_validate_fails_metadata_empty_dict(create_tx):
    create_tx.metadata = {'a': 1}
    validate_transaction_schema(create_tx.to_dict())
    create_tx.metadata = None
    validate_transaction_schema(create_tx.to_dict())
    create_tx.metadata = {}
    with raises(SchemaValidationError):
        validate_transaction_schema(create_tx.to_dict())


def test_transfer_asset_schema(signed_transfer_tx):
    tx = signed_transfer_tx.to_dict()
    validate_transaction_schema(tx)
    tx['asset']['data'] = {}
    with raises(SchemaValidationError):
        validate_transaction_schema(tx)
    del tx['asset']['data']
    tx['asset']['id'] = 'b' * 63
    with raises(SchemaValidationError):
        validate_transaction_schema(tx)


def test_create_single_input(create_tx):
    tx = create_tx.to_dict()
    tx['inputs'] += tx['inputs']
    with raises(SchemaValidationError):
        validate_transaction_schema(tx)
    tx['inputs'] = []
    with raises(SchemaValidationError):
        validate_transaction_schema(tx)


def test_create_tx_no_fulfills(create_tx):
    tx = create_tx.to_dict()
    tx['inputs'][0]['fulfills'] = {'tx': 'a' * 64, 'output': 0}
    with raises(SchemaValidationError):
        validate_transaction_schema(tx)
