from pytest import raises


def test_input_serialization(ffill_uri, user_pub):
    from bigchaindb.common.transaction import Input

    expected = {
        'fulfillment': ffill_uri,
    }
    input = Input(ffill_uri)
    assert input.to_dict() == expected


def test_input_deserialization_with_uri(ffill_uri):
    from bigchaindb.common.transaction import Input

    expected = Input(ffill_uri)
    ffill = {
        'fulfillment': ffill_uri,
    }
    input = Input.from_dict(ffill)

    assert input == expected


def test_output_serialization(user_pub):
    from bigchaindb.common.transaction import Output

    expected = {
        'condition': {
            'structure': '%0',
            'pubkeys': [user_pub],
        },
        'amount': 1,
    }

    cond = Output.generate([user_pub], 1)

    assert cond.to_dict() == expected


def test_output_deserialization(user_Ed25519, user_pub):
    from bigchaindb.common.transaction import Output

    expected = Output.generate([user_pub], 1)
    cond = {
        'condition': {
            'structure': '%0',
            'pubkeys': [user_pub],
        },
        'amount': 1,
    }
    cond = Output.from_dict(cond)

    assert cond == expected


def test_generate_output_invalid_parameters(user_pub, user2_pub, user3_pub):
    from bigchaindb.common.transaction import Output

    with raises(ValueError):
        Output.generate([], 1)
    with raises(TypeError):
        Output.generate('not a list', 1)
    with raises(ValueError):
        Output.generate([[user_pub, [user2_pub, [user3_pub]]]], 1)
    with raises(ValueError):
        Output.generate([[user_pub]], 1)


def test_invalid_transaction_initialization(asset_definition):
    from bigchaindb.common.transaction import Transaction

    with raises(ValueError):
        Transaction(operation='invalid operation', asset=asset_definition)
    with raises(TypeError):
        Transaction(operation='CREATE', asset='invalid asset')
    with raises(TypeError):
        Transaction(operation='TRANSFER', asset={})
    with raises(TypeError):
        Transaction(
            operation='CREATE',
            asset=asset_definition,
            outputs='invalid outputs'
        )
    with raises(TypeError):
        Transaction(
            operation='CREATE',
            asset=asset_definition,
            outputs=[],
            inputs='invalid inputs'
        )
    with raises(TypeError):
        Transaction(
            operation='CREATE',
            asset=asset_definition,
            outputs=[],
            inputs=[],
            metadata='invalid metadata'
        )


def test_create_default_asset_on_tx_initialization(asset_definition):
    from bigchaindb.common.transaction import Transaction

    expected = {'data': None}
    tx = Transaction(Transaction.CREATE, asset=expected)
    asset = tx.asset

    assert asset == expected


def test_transaction_serialization(user_input, user_output, data):
    from bigchaindb.common.transaction import Transaction

    tx_id = 'l0l'

    expected = {
        'id': tx_id,
        'version': Transaction.VERSION,
        # NOTE: This test assumes that Inputs and Outputs can
        #       successfully be serialized
        'inputs': [user_input.to_dict()],
        'outputs': [user_output.to_dict()],
        'operation': Transaction.CREATE,
        'metadata': None,
        'asset': {
            'data': data,
        }
    }

    tx = Transaction(Transaction.CREATE, {'data': data}, [user_input],
                     [user_output])
    tx_dict = tx.to_dict()
    tx_dict['id'] = tx_id

    assert tx_dict == expected


def test_transaction_deserialization(user_input, user_output, data):
    from bigchaindb.common.transaction import Transaction
    from .utils import validate_transaction_model

    expected_asset = {'data': data}
    expected = Transaction(Transaction.CREATE, expected_asset, [user_input],
                           [user_output], None, Transaction.VERSION)

    tx = {
        'version': Transaction.VERSION,
        # NOTE: This test assumes that Inputs and Outputs can
        #       successfully be serialized
        'inputs': [user_input.to_dict()],
        'outputs': [user_output.to_dict()],
        'operation': Transaction.CREATE,
        'metadata': None,
        'asset': {
            'data': data,
        }
    }
    tx_no_signatures = Transaction._remove_signatures(tx)
    tx['id'] = Transaction._to_hash(Transaction._to_str(tx_no_signatures))
    tx = Transaction.from_dict(tx)

    assert tx == expected

    validate_transaction_model(tx)


def test_tx_serialization_with_incorrect_hash(utx):
    from bigchaindb.common.transaction import Transaction
    from bigchaindb.common.exceptions import InvalidHash

    utx_dict = utx.to_dict()
    utx_dict['id'] = 'a' * 64
    with raises(InvalidHash):
        Transaction.from_dict(utx_dict)
    utx_dict.pop('id')


def test_tx_serialization_hash_function(tx):
    import sha3
    import json
    tx_dict = tx.to_dict()
    tx_dict['inputs'][0]['fulfillment'] = None
    del tx_dict['id']
    payload = json.dumps(tx_dict, skipkeys=False, sort_keys=True,
                         separators=(',', ':'))
    assert sha3.sha3_256(payload.encode()).hexdigest() == tx.id


def test_invalid_input_initialization(user_input, user_pub):
    from bigchaindb.common.transaction import Input

    with raises(TypeError):
        Input(user_input, user_pub)
    with raises(TypeError):
        Input(user_input, tx_input='somethingthatiswrong')


def test_transaction_link_serialization():
    from bigchaindb.common.transaction import TransactionLink

    tx_id = 'a transaction id'
    expected = {
        'txid': tx_id,
        'output': 0,
    }
    tx_link = TransactionLink(tx_id, 0)

    assert tx_link.to_dict() == expected


def test_transaction_link_serialization_with_empty_payload():
    from bigchaindb.common.transaction import TransactionLink

    expected = None
    tx_link = TransactionLink()

    assert tx_link.to_dict() == expected


def test_transaction_link_deserialization():
    from bigchaindb.common.transaction import TransactionLink

    tx_id = 'a transaction id'
    expected = TransactionLink(tx_id, 0)
    tx_link = {
        'txid': tx_id,
        'output': 0,
    }
    tx_link = TransactionLink.from_dict(tx_link)

    assert tx_link == expected


def test_transaction_link_deserialization_with_empty_payload():
    from bigchaindb.common.transaction import TransactionLink

    expected = TransactionLink()
    tx_link = TransactionLink.from_dict(None)

    assert tx_link == expected


def test_transaction_link_empty_to_uri():
    from bigchaindb.common.transaction import TransactionLink

    expected = None
    tx_link = TransactionLink().to_uri()

    assert expected == tx_link


def test_transaction_link_to_uri():
    from bigchaindb.common.transaction import TransactionLink

    expected = 'path/transactions/abc/outputs/0'
    tx_link = TransactionLink('abc', 0).to_uri('path')

    assert expected == tx_link


def test_cast_transaction_link_to_boolean():
    from bigchaindb.common.transaction import TransactionLink

    assert bool(TransactionLink()) is False
    assert bool(TransactionLink('a', None)) is False
    assert bool(TransactionLink(None, 'b')) is False
    assert bool(TransactionLink('a', 'b')) is True
    assert bool(TransactionLink(False, False)) is True


def test_transaction_link_eq():
    from bigchaindb.common.transaction import TransactionLink

    assert TransactionLink(1, 2) == TransactionLink(1, 2)
    assert TransactionLink(2, 2) != TransactionLink(1, 2)
    assert TransactionLink(1, 1) != TransactionLink(1, 2)
    assert TransactionLink(2, 1) != TransactionLink(1, 2)


def test_add_input_to_tx(user_input, asset_definition):
    from bigchaindb.common.transaction import Transaction
    from .utils import validate_transaction_model

    tx = Transaction(Transaction.CREATE, asset_definition, [], [])
    tx.add_input(user_input)

    assert len(tx.inputs) == 1

    validate_transaction_model(tx)


def test_add_input_to_tx_with_invalid_parameters(asset_definition):
    from bigchaindb.common.transaction import Transaction
    tx = Transaction(Transaction.CREATE, asset_definition)

    with raises(TypeError):
        tx.add_input('somewronginput')


def test_add_output_to_tx(user_output, user_input, asset_definition):
    from bigchaindb.common.transaction import Transaction
    from .utils import validate_transaction_model

    tx = Transaction(Transaction.CREATE, asset_definition, [user_input])
    tx.add_output(user_output)

    assert len(tx.outputs) == 1

    validate_transaction_model(tx)


def test_add_output_to_tx_with_invalid_parameters(asset_definition):
    from bigchaindb.common.transaction import Transaction
    tx = Transaction(Transaction.CREATE, asset_definition, [], [])

    with raises(TypeError):
        tx.add_output('somewronginput')


def test_sign_with_invalid_parameters(utx, user_priv):
    with raises(TypeError):
        utx.sign(None)
    with raises(TypeError):
        utx.sign(user_priv)


def test_create_create_transaction_single_io(user_output, user_pub, data):
    from bigchaindb.common.transaction import Transaction
    from .utils import validate_transaction_model

    expected = {
        'outputs': [user_output.to_dict()],
        'metadata': data,
        'asset': {
            'data': data,
        },
        'inputs': [
            {
                'fulfillment': None,
            }
        ],
        'operation': 'CREATE',
        'version': Transaction.VERSION,
    }

    tx = Transaction.create([user_pub], [([user_pub], 1)], metadata=data,
                            asset=data)
    tx_dict = tx.to_dict()
    tx_dict['inputs'][0]['fulfillment'] = None
    tx_dict.pop('id')

    assert tx_dict == expected

    validate_transaction_model(tx)


def test_validate_single_io_create_transaction(user_pub, user_priv, data,
                                               asset_definition):
    from bigchaindb.common.transaction import Transaction

    tx = Transaction.create([user_pub], [([user_pub], 1)], metadata=data)
    tx = tx.sign([user_priv])
    assert tx.inputs_valid() is True


def test_create_create_transaction_multiple_io(user_output, user2_output, user_pub,
                                               user2_pub, asset_definition):
    from bigchaindb.common.transaction import Transaction, Input

    # a fulfillment for a create transaction with multiple `owners_before`
    # is a fulfillment for an implicit threshold condition with
    # weight = len(owners_before)
    input = Input.generate([user_pub, user2_pub]).to_dict()
    expected = {
        'outputs': [user_output.to_dict(), user2_output.to_dict()],
        'metadata': {
            'message': 'hello'
        },
        'inputs': [input],
        'operation': 'CREATE',
        'version': Transaction.VERSION
    }
    tx = Transaction.create([user_pub, user2_pub],
                            [([user_pub], 1), ([user2_pub], 1)],
                            metadata={'message': 'hello'}).to_dict()
    tx.pop('id')
    tx.pop('asset')

    assert tx == expected


def test_validate_multiple_io_create_transaction(user_pub, user_priv,
                                                 user2_pub, user2_priv,
                                                 asset_definition):
    from bigchaindb.common.transaction import Transaction
    from .utils import validate_transaction_model

    tx = Transaction.create([user_pub, user2_pub],
                            [([user_pub], 1), ([user2_pub], 1)],
                            metadata={'message': 'hello'})
    tx = tx.sign([user_priv, user2_priv])
    assert tx.inputs_valid() is True

    validate_transaction_model(tx)


def test_create_create_transaction_threshold(user_pub, user2_pub, user3_pub,
                                             user_user2_threshold_output,
                                             user_user2_threshold_input, data):
    from bigchaindb.common.transaction import Transaction

    expected = {
        'outputs': [user_user2_threshold_output.to_dict()],
        'metadata': data,
        'asset': {
            'data': data,
        },
        'inputs': [
            {
                'fulfillment': None,
            },
        ],
        'operation': 'CREATE',
        'version': Transaction.VERSION
    }
    tx = Transaction.create([user_pub], [([user_pub, user2_pub], 1)],
                            metadata=data, asset=data)
    tx_dict = tx.to_dict()
    tx_dict.pop('id')
    tx_dict['inputs'][0]['fulfillment'] = None

    assert tx_dict == expected


def test_validate_threshold_create_transaction(user_pub, user_priv, user2_pub,
                                               data, asset_definition):
    from bigchaindb.common.transaction import Transaction
    from .utils import validate_transaction_model

    tx = Transaction.create([user_pub], [([user_pub, user2_pub], 1)],
                            metadata=data)
    tx = tx.sign([user_priv])
    assert tx.inputs_valid() is True

    validate_transaction_model(tx)


def test_create_create_transaction_with_invalid_parameters(user_pub):
    from bigchaindb.common.transaction import Transaction

    with raises(TypeError):
        Transaction.create('not a list')
    with raises(TypeError):
        Transaction.create([], 'not a list')
    with raises(ValueError):
        Transaction.create([], [user_pub])
    with raises(ValueError):
        Transaction.create([user_pub], [])
    with raises(ValueError):
        Transaction.create([user_pub], [user_pub])
    with raises(ValueError):
        Transaction.create([user_pub], [([user_pub],)])
    with raises(TypeError):
        Transaction.create([user_pub], [([user_pub], 1)],
                           metadata='not a dict or none')
    with raises(TypeError):
        Transaction.create([user_pub],
                           [([user_pub], 1)],
                           asset='not a dict or none')


def test_outputs_to_inputs(tx):
    inputs = tx.to_inputs([0])
    assert len(inputs) == 1
    input = inputs.pop()
    assert input.condition == tx.outputs[0].condition
    assert input.fulfills.txid == tx.id
    assert input.fulfills.output == 0


def test_create_transfer_transaction_single_io(tx, user_pub, user2_pub,
                                               user2_output, user_priv):
    from copy import deepcopy
    from bigchaindb.common.transaction import Transaction
    from bigchaindb.common.utils import serialize
    from .utils import validate_transaction_model

    expected = {
        'outputs': [user2_output.to_dict()],
        'metadata': None,
        'asset': {
            'id': tx.id,
        },
        'inputs': [
            {
                'fulfillment': None,
                'fulfills': {
                    'txid': tx.id,
                    'output': 0
                }
            }
        ],
        'operation': 'TRANSFER',
        'version': Transaction.VERSION
    }
    inputs = tx.to_inputs([0])
    transfer_tx = Transaction.transfer(inputs, [([user2_pub], 1)],
                                       asset_id=tx.id)
    transfer_tx = transfer_tx.sign([user_priv])
    transfer_tx = transfer_tx.to_dict()

    expected_input = deepcopy(inputs[0])
    expected['id'] = transfer_tx['id']
    msg = '0:' + serialize(expected)
    expected_ffill = expected_input.sign([user_priv], msg).fulfillment
    transfer_ffill = transfer_tx['inputs'][0]['fulfillment']

    assert transfer_ffill == expected_ffill

    transfer_tx = Transaction.from_dict(transfer_tx)
    assert transfer_tx.inputs_valid([tx.outputs[0]]) is True

    validate_transaction_model(transfer_tx)


def test_create_transfer_transaction_multiple_io(user_pub, user_priv,
                                                 user2_pub, user2_priv,
                                                 user3_pub, user2_output,
                                                 asset_definition):
    from bigchaindb.common.transaction import Transaction

    tx = Transaction.create([user_pub], [([user_pub], 1), ([user2_pub], 1)],
                            metadata={'message': 'hello'})
    tx = tx.sign([user_priv])

    expected = {
        'outputs': [user2_output.to_dict(), user2_output.to_dict()],
        'metadata': None,
        'inputs': [
            {
                'fulfillment': None,
                'fulfills': {
                    'txid': tx.id,
                    'output': 0
                }
            }, {
                'fulfillment': None,
                'fulfills': {
                    'txid': tx.id,
                    'output': 1
                }
            }
        ],
        'operation': 'TRANSFER',
        'version': Transaction.VERSION
    }

    transfer_tx = Transaction.transfer(tx.to_inputs(),
                                       [([user2_pub], 1), ([user2_pub], 1)],
                                       asset_id=tx.id)
    transfer_tx = transfer_tx.sign([user_priv, user2_priv])

    assert len(transfer_tx.inputs) == 2
    assert len(transfer_tx.outputs) == 2

    assert transfer_tx.inputs_valid(tx.outputs) is True

    transfer_tx = transfer_tx.to_dict()
    transfer_tx['inputs'][0]['fulfillment'] = None
    transfer_tx['inputs'][1]['fulfillment'] = None
    transfer_tx.pop('asset')
    transfer_tx.pop('id')

    assert expected == transfer_tx


def test_create_transfer_with_invalid_parameters(tx, user_pub):
    from bigchaindb.common.transaction import Transaction

    with raises(TypeError):
        Transaction.transfer({}, [], tx.id)
    with raises(ValueError):
        Transaction.transfer([], [], tx.id)
    with raises(TypeError):
        Transaction.transfer(['fulfillment'], {}, tx.id)
    with raises(ValueError):
        Transaction.transfer(['fulfillment'], [], tx.id)
    with raises(ValueError):
        Transaction.transfer(['fulfillment'], [user_pub], tx.id)
    with raises(ValueError):
        Transaction.transfer(['fulfillment'], [([user_pub],)], tx.id)
    with raises(TypeError):
        Transaction.transfer(['fulfillment'], [([user_pub], 1)],
                             tx.id, metadata='not a dict or none')
    with raises(TypeError):
        Transaction.transfer(['fulfillment'], [([user_pub], 1)],
                             ['not a string'])


def test_cant_add_empty_output():
    from bigchaindb.common.transaction import Transaction
    tx = Transaction(Transaction.CREATE, None)

    with raises(TypeError):
        tx.add_output(None)


def test_cant_add_empty_input():
    from bigchaindb.common.transaction import Transaction
    tx = Transaction(Transaction.CREATE, None)

    with raises(TypeError):
        tx.add_input(None)


def test_validate_version(utx):
    import re
    import bigchaindb.version
    from .utils import validate_transaction_model
    from bigchaindb.common.exceptions import SchemaValidationError

    short_ver = bigchaindb.version.__short_version__
    assert utx.version == re.match(r'^(.*\d)', short_ver).group(1)

    validate_transaction_model(utx)

    # At version 1, transaction version will break step with server version.
    utx.version = '1.0.0'
    with raises(SchemaValidationError):
        validate_transaction_model(utx)


def test_create_tx_no_asset_id(b, utx):
    from bigchaindb.common.exceptions import SchemaValidationError
    from .utils import validate_transaction_model
    utx.asset['id'] = 'b' * 64
    with raises(SchemaValidationError):
        validate_transaction_model(utx)


def test_transfer_tx_asset_schema(transfer_utx):
    from bigchaindb.common.exceptions import SchemaValidationError
    from .utils import validate_transaction_model
    tx = transfer_utx
    tx.asset['data'] = {}
    with raises(SchemaValidationError):
        validate_transaction_model(tx)


# TODO
import pytest
@pytest.mark.skip('TODO')
def test_write_new_sign_verify_tests():
    # include tests for condition dsl and parse errors
    raise NotImplementedError


def test_create_transaction_verify_unicode(b):
    from bigchaindb.common.transaction import Transaction

    tx = Transaction.create([b.me], [([b.me], 1)],
                            metadata={'a': '\N{HAMSTER FACE}'})
    tx = tx.sign([b.me_private])
    assert tx.inputs_valid()
