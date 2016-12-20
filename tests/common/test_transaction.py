from pytest import raises
from unittest.mock import patch


def test_fulfillment_serialization(ffill_uri, user_pub):
    from bigchaindb.common.transaction import Fulfillment
    from cryptoconditions import Fulfillment as CCFulfillment

    expected = {
        'owners_before': [user_pub],
        'fulfillment': ffill_uri,
        'input': None,
    }
    ffill = Fulfillment(CCFulfillment.from_uri(ffill_uri), [user_pub])
    assert ffill.to_dict() == expected


def test_fulfillment_deserialization_with_uri(ffill_uri, user_pub):
    from bigchaindb.common.transaction import Fulfillment
    from cryptoconditions import Fulfillment as CCFulfillment

    expected = Fulfillment(CCFulfillment.from_uri(ffill_uri), [user_pub])
    ffill = {
        'owners_before': [user_pub],
        'fulfillment': ffill_uri,
        'input': None,
    }
    ffill = Fulfillment.from_dict(ffill)

    assert ffill == expected


def test_fulfillment_deserialization_with_invalid_fulfillment(user_pub):
    from bigchaindb.common.transaction import Fulfillment

    ffill = {
        'owners_before': [user_pub],
        'fulfillment': None,
        'input': None,
    }
    with raises(TypeError):
        Fulfillment.from_dict(ffill)


def test_fulfillment_deserialization_with_invalid_fulfillment_uri(user_pub):
    from bigchaindb.common.exceptions import InvalidSignature
    from bigchaindb.common.transaction import Fulfillment

    ffill = {
        'owners_before': [user_pub],
        'fulfillment': 'an invalid fulfillment',
        'input': None,
    }
    with raises(InvalidSignature):
        Fulfillment.from_dict(ffill)


def test_fulfillment_deserialization_with_unsigned_fulfillment(ffill_uri,
                                                               user_pub):
    from bigchaindb.common.transaction import Fulfillment
    from cryptoconditions import Fulfillment as CCFulfillment

    expected = Fulfillment(CCFulfillment.from_uri(ffill_uri), [user_pub])
    ffill = {
        'owners_before': [user_pub],
        'fulfillment': CCFulfillment.from_uri(ffill_uri),
        'input': None,
    }
    ffill = Fulfillment.from_dict(ffill)

    assert ffill == expected


def test_condition_serialization(user_Ed25519, user_pub):
    from bigchaindb.common.transaction import Condition

    expected = {
        'condition': {
            'uri': user_Ed25519.condition_uri,
            'details': user_Ed25519.to_dict(),
        },
        'owners_after': [user_pub],
        'amount': 1,
    }

    cond = Condition(user_Ed25519, [user_pub], 1)

    assert cond.to_dict() == expected


def test_condition_deserialization(user_Ed25519, user_pub):
    from bigchaindb.common.transaction import Condition

    expected = Condition(user_Ed25519, [user_pub], 1)
    cond = {
        'condition': {
            'uri': user_Ed25519.condition_uri,
            'details': user_Ed25519.to_dict()
        },
        'owners_after': [user_pub],
        'amount': 1,
    }
    cond = Condition.from_dict(cond)

    assert cond == expected


def test_condition_hashlock_serialization():
    from bigchaindb.common.transaction import Condition
    from cryptoconditions import PreimageSha256Fulfillment

    secret = b'wow much secret'
    hashlock = PreimageSha256Fulfillment(preimage=secret).condition_uri

    expected = {
        'condition': {
            'uri': hashlock,
        },
        'owners_after': None,
        'amount': 1,
    }
    cond = Condition(hashlock, amount=1)

    assert cond.to_dict() == expected


def test_condition_hashlock_deserialization():
    from bigchaindb.common.transaction import Condition
    from cryptoconditions import PreimageSha256Fulfillment

    secret = b'wow much secret'
    hashlock = PreimageSha256Fulfillment(preimage=secret).condition_uri
    expected = Condition(hashlock, amount=1)

    cond = {
        'condition': {
            'uri': hashlock
        },
        'owners_after': None,
        'amount': 1,
    }
    cond = Condition.from_dict(cond)

    assert cond == expected


def test_invalid_condition_initialization(cond_uri, user_pub):
    from bigchaindb.common.transaction import Condition

    with raises(TypeError):
        Condition(cond_uri, user_pub)


def test_generate_conditions_split_half_recursive(user_pub, user2_pub,
                                                  user3_pub):
    from bigchaindb.common.transaction import Condition
    from cryptoconditions import Ed25519Fulfillment, ThresholdSha256Fulfillment

    expected_simple1 = Ed25519Fulfillment(public_key=user_pub)
    expected_simple2 = Ed25519Fulfillment(public_key=user2_pub)
    expected_simple3 = Ed25519Fulfillment(public_key=user3_pub)

    expected = ThresholdSha256Fulfillment(threshold=2)
    expected.add_subfulfillment(expected_simple1)
    expected_threshold = ThresholdSha256Fulfillment(threshold=2)
    expected_threshold.add_subfulfillment(expected_simple2)
    expected_threshold.add_subfulfillment(expected_simple3)
    expected.add_subfulfillment(expected_threshold)

    cond = Condition.generate([user_pub, [user2_pub, expected_simple3]], 1)
    assert cond.fulfillment.to_dict() == expected.to_dict()


def test_generate_conditions_split_half_single_owner(user_pub, user2_pub,
                                                     user3_pub):
    from bigchaindb.common.transaction import Condition
    from cryptoconditions import Ed25519Fulfillment, ThresholdSha256Fulfillment

    expected_simple1 = Ed25519Fulfillment(public_key=user_pub)
    expected_simple2 = Ed25519Fulfillment(public_key=user2_pub)
    expected_simple3 = Ed25519Fulfillment(public_key=user3_pub)

    expected = ThresholdSha256Fulfillment(threshold=2)
    expected_threshold = ThresholdSha256Fulfillment(threshold=2)
    expected_threshold.add_subfulfillment(expected_simple2)
    expected_threshold.add_subfulfillment(expected_simple3)
    expected.add_subfulfillment(expected_threshold)
    expected.add_subfulfillment(expected_simple1)

    cond = Condition.generate([[expected_simple2, user3_pub], user_pub], 1)
    assert cond.fulfillment.to_dict() == expected.to_dict()


def test_generate_conditions_flat_ownage(user_pub, user2_pub, user3_pub):
    from bigchaindb.common.transaction import Condition
    from cryptoconditions import Ed25519Fulfillment, ThresholdSha256Fulfillment

    expected_simple1 = Ed25519Fulfillment(public_key=user_pub)
    expected_simple2 = Ed25519Fulfillment(public_key=user2_pub)
    expected_simple3 = Ed25519Fulfillment(public_key=user3_pub)

    expected = ThresholdSha256Fulfillment(threshold=3)
    expected.add_subfulfillment(expected_simple1)
    expected.add_subfulfillment(expected_simple2)
    expected.add_subfulfillment(expected_simple3)

    cond = Condition.generate([user_pub, user2_pub, expected_simple3], 1)
    assert cond.fulfillment.to_dict() == expected.to_dict()


def test_generate_conditions_single_owner(user_pub):
    from bigchaindb.common.transaction import Condition
    from cryptoconditions import Ed25519Fulfillment

    expected = Ed25519Fulfillment(public_key=user_pub)
    cond = Condition.generate([user_pub], 1)

    assert cond.fulfillment.to_dict() == expected.to_dict()


def test_generate_conditions_single_owner_with_condition(user_pub):
    from bigchaindb.common.transaction import Condition
    from cryptoconditions import Ed25519Fulfillment

    expected = Ed25519Fulfillment(public_key=user_pub)
    cond = Condition.generate([expected], 1)

    assert cond.fulfillment.to_dict() == expected.to_dict()


def test_generate_conditions_invalid_parameters(user_pub, user2_pub,
                                                user3_pub):
    from bigchaindb.common.transaction import Condition

    with raises(ValueError):
        Condition.generate([], 1)
    with raises(TypeError):
        Condition.generate('not a list', 1)
    with raises(ValueError):
        Condition.generate([[user_pub, [user2_pub, [user3_pub]]]], 1)
    with raises(ValueError):
        Condition.generate([[user_pub]], 1)


def test_invalid_transaction_initialization():
    from bigchaindb.common.transaction import Transaction, Asset

    with raises(ValueError):
        Transaction(operation='invalid operation', asset=Asset())
    with raises(TypeError):
        Transaction(operation='CREATE', asset='invalid asset')
    with raises(TypeError):
        Transaction(
            operation='CREATE',
            asset=Asset(),
            conditions='invalid conditions'
        )
    with raises(TypeError):
        Transaction(
            operation='CREATE',
            asset=Asset(),
            conditions=[],
            fulfillments='invalid fulfillments'
        )
    with raises(TypeError):
        Transaction(
            operation='CREATE',
            asset=Asset(),
            conditions=[],
            fulfillments=[],
            metadata='invalid metadata'
        )


def test_create_default_asset_on_tx_initialization():
    from bigchaindb.common.transaction import Transaction, Asset
    from bigchaindb.common.exceptions import ValidationError
    from .util import validate_transaction_model

    with patch.object(Asset, 'validate_asset', return_value=None):
        tx = Transaction(Transaction.CREATE, None)
    expected = Asset()
    asset = tx.asset

    expected.data_id = None
    asset.data_id = None
    assert asset == expected

    # Fails because no asset hash
    with raises(ValidationError):
        validate_transaction_model(tx)


def test_transaction_serialization(user_ffill, user_cond, data, data_id):
    from bigchaindb.common.transaction import Transaction, Asset
    from bigchaindb.common.exceptions import ValidationError
    from .util import validate_transaction_model

    tx_id = 'l0l'

    expected = {
        'id': tx_id,
        'version': Transaction.VERSION,
        # NOTE: This test assumes that Fulfillments and Conditions can
        #       successfully be serialized
        'fulfillments': [user_ffill.to_dict()],
        'conditions': [user_cond.to_dict()],
        'operation': Transaction.CREATE,
        'metadata': None,
        'asset': {
            'id': data_id,
            'data': data,
        }
    }

    tx = Transaction(Transaction.CREATE, Asset(data, data_id), [user_ffill],
                     [user_cond])
    tx_dict = tx.to_dict()
    tx_dict['id'] = tx_id
    tx_dict['asset']['id'] = data_id

    assert tx_dict == expected

    # Fails because asset id is not a uuid4
    with raises(ValidationError):
        validate_transaction_model(tx)


def test_transaction_deserialization(user_ffill, user_cond, data, uuid4):
    from bigchaindb.common.transaction import Transaction, Asset
    from .util import validate_transaction_model


    expected_asset = Asset(data, uuid4)
    expected = Transaction(Transaction.CREATE, expected_asset, [user_ffill],
                           [user_cond], None, Transaction.VERSION)

    tx = {
        'version': Transaction.VERSION,
        # NOTE: This test assumes that Fulfillments and Conditions can
        #       successfully be serialized
        'fulfillments': [user_ffill.to_dict()],
        'conditions': [user_cond.to_dict()],
        'operation': Transaction.CREATE,
        'metadata': None,
        'asset': {
            'id': uuid4,
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


def test_invalid_fulfillment_initialization(user_ffill, user_pub):
    from bigchaindb.common.transaction import Fulfillment

    with raises(TypeError):
        Fulfillment(user_ffill, user_pub)
    with raises(TypeError):
        Fulfillment(user_ffill, [], tx_input='somethingthatiswrong')


def test_transaction_link_serialization():
    from bigchaindb.common.transaction import TransactionLink

    tx_id = 'a transaction id'
    expected = {
        'txid': tx_id,
        'cid': 0,
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
        'cid': 0,
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

    expected = 'path/transactions/abc/conditions/0'
    tx_link = TransactionLink('abc', 0).to_uri('path')

    assert expected == tx_link


def test_cast_transaction_link_to_boolean():
    from bigchaindb.common.transaction import TransactionLink

    assert bool(TransactionLink()) is False
    assert bool(TransactionLink('a', None)) is False
    assert bool(TransactionLink(None, 'b')) is False
    assert bool(TransactionLink('a', 'b')) is True
    assert bool(TransactionLink(False, False)) is True


def test_asset_link_serialization():
    from bigchaindb.common.transaction import AssetLink

    data_id = 'a asset id'
    expected = {
        'id': data_id,
    }
    asset_link = AssetLink(data_id)

    assert asset_link.to_dict() == expected


def test_asset_link_serialization_with_empty_payload():
    from bigchaindb.common.transaction import AssetLink

    expected = None
    asset_link = AssetLink()

    assert asset_link.to_dict() == expected


def test_asset_link_deserialization():
    from bigchaindb.common.transaction import AssetLink

    data_id = 'a asset id'
    expected = AssetLink(data_id)
    asset_link = {
        'id': data_id
    }
    asset_link = AssetLink.from_dict(asset_link)

    assert asset_link == expected


def test_asset_link_deserialization_with_empty_payload():
    from bigchaindb.common.transaction import AssetLink

    expected = AssetLink()
    asset_link = AssetLink.from_dict(None)

    assert asset_link == expected


def test_cast_asset_link_to_boolean():
    from bigchaindb.common.transaction import AssetLink

    assert bool(AssetLink()) is False
    assert bool(AssetLink('a')) is True
    assert bool(AssetLink(False)) is True


def test_eq_asset_link():
    from bigchaindb.common.transaction import AssetLink

    asset_id_1 = 'asset_1'
    asset_id_2 = 'asset_2'

    assert AssetLink(asset_id_1) == AssetLink(asset_id_1)
    assert AssetLink(asset_id_1) != AssetLink(asset_id_2)


def test_add_fulfillment_to_tx(user_ffill):
    from bigchaindb.common.transaction import Transaction, Asset

    with patch.object(Asset, 'validate_asset', return_value=None):
        tx = Transaction(Transaction.CREATE, Asset(), [], [])
    tx.add_fulfillment(user_ffill)

    assert len(tx.fulfillments) == 1


def test_add_fulfillment_to_tx_with_invalid_parameters():
    from bigchaindb.common.transaction import Transaction, Asset

    with patch.object(Asset, 'validate_asset', return_value=None):
        tx = Transaction(Transaction.CREATE, Asset())
    with raises(TypeError):
        tx.add_fulfillment('somewronginput')


def test_add_condition_to_tx(user_cond):
    from bigchaindb.common.transaction import Transaction, Asset
    from .util import validate_transaction_model

    with patch.object(Asset, 'validate_asset', return_value=None):
        tx = Transaction(Transaction.CREATE, Asset())
    tx.add_condition(user_cond)

    assert len(tx.conditions) == 1

    validate_transaction_model(tx)


def test_add_condition_to_tx_with_invalid_parameters():
    from bigchaindb.common.transaction import Transaction, Asset

    with patch.object(Asset, 'validate_asset', return_value=None):
        tx = Transaction(Transaction.CREATE, Asset(), [], [])
    with raises(TypeError):
        tx.add_condition('somewronginput')


def test_sign_with_invalid_parameters(utx, user_priv):
    with raises(TypeError):
        utx.sign(None)
    with raises(TypeError):
        utx.sign(user_priv)


def test_validate_tx_simple_create_signature(user_ffill, user_cond, user_priv):
    from copy import deepcopy
    from bigchaindb.common.crypto import PrivateKey
    from bigchaindb.common.transaction import Transaction, Asset
    from .util import validate_transaction_model

    tx = Transaction(Transaction.CREATE, Asset(), [user_ffill], [user_cond])
    expected = deepcopy(user_cond)
    expected.fulfillment.sign(str(tx).encode(), PrivateKey(user_priv))
    tx.sign([user_priv])

    assert tx.fulfillments[0].to_dict()['fulfillment'] == \
        expected.fulfillment.serialize_uri()
    assert tx.fulfillments_valid() is True

    validate_transaction_model(tx)


def test_invoke_simple_signature_fulfillment_with_invalid_params(utx,
                                                                 user_ffill):
    from bigchaindb.common.exceptions import KeypairMismatchException

    with raises(KeypairMismatchException):
        invalid_key_pair = {'wrong_pub_key': 'wrong_priv_key'}
        utx._sign_simple_signature_fulfillment(user_ffill,
                                               0,
                                               'somemessage',
                                               invalid_key_pair)


def test_sign_threshold_with_invalid_params(utx, user_user2_threshold_ffill,
                                            user3_pub, user3_priv):
    from bigchaindb.common.exceptions import KeypairMismatchException

    with raises(KeypairMismatchException):
        utx._sign_threshold_signature_fulfillment(user_user2_threshold_ffill,
                                                  0,
                                                  'somemessage',
                                                  {user3_pub: user3_priv})
    with raises(KeypairMismatchException):
        user_user2_threshold_ffill.owners_before = ['somewrongvalue']
        utx._sign_threshold_signature_fulfillment(user_user2_threshold_ffill,
                                                  0,
                                                  'somemessage',
                                                  None)


def test_validate_fulfillment_with_invalid_parameters(utx):
    from bigchaindb.common.transaction import Transaction

    input_conditions = [cond.fulfillment.condition_uri for cond
                        in utx.conditions]
    tx_dict = utx.to_dict()
    tx_dict = Transaction._remove_signatures(tx_dict)
    tx_serialized = Transaction._to_str(tx_dict)
    assert utx._fulfillment_valid(utx.fulfillments[0],
                                  tx_serialized,
                                  input_conditions) is False


def test_validate_multiple_fulfillments(user_ffill, user_cond, user_priv):
    from copy import deepcopy

    from bigchaindb.common.crypto import PrivateKey
    from bigchaindb.common.transaction import Transaction, Asset
    from .util import validate_transaction_model

    tx = Transaction(Transaction.CREATE, Asset(),
                     [user_ffill, deepcopy(user_ffill)],
                     [user_cond, deepcopy(user_cond)])

    expected_first = deepcopy(tx)
    expected_second = deepcopy(tx)
    expected_first.fulfillments = [expected_first.fulfillments[0]]
    expected_second.fulfillments = [expected_second.fulfillments[1]]

    expected_first_bytes = str(expected_first).encode()
    expected_first.fulfillments[0].fulfillment.sign(expected_first_bytes,
                                                    PrivateKey(user_priv))
    expected_second_bytes = str(expected_second).encode()
    expected_second.fulfillments[0].fulfillment.sign(expected_second_bytes,
                                                     PrivateKey(user_priv))
    tx.sign([user_priv])

    assert tx.fulfillments[0].to_dict()['fulfillment'] == \
        expected_first.fulfillments[0].fulfillment.serialize_uri()
    assert tx.fulfillments[1].to_dict()['fulfillment'] == \
        expected_second.fulfillments[0].fulfillment.serialize_uri()
    assert tx.fulfillments_valid() is True

    validate_transaction_model(tx)


def test_validate_tx_threshold_create_signature(user_user2_threshold_ffill,
                                                user_user2_threshold_cond,
                                                user_pub,
                                                user2_pub,
                                                user_priv,
                                                user2_priv):
    from copy import deepcopy

    from bigchaindb.common.crypto import PrivateKey
    from bigchaindb.common.transaction import Transaction, Asset
    from .util import validate_transaction_model

    tx = Transaction(Transaction.CREATE, Asset(), [user_user2_threshold_ffill],
                     [user_user2_threshold_cond])
    expected = deepcopy(user_user2_threshold_cond)
    expected.fulfillment.subconditions[0]['body'].sign(str(tx).encode(),
                                                       PrivateKey(user_priv))
    expected.fulfillment.subconditions[1]['body'].sign(str(tx).encode(),
                                                       PrivateKey(user2_priv))
    tx.sign([user_priv, user2_priv])

    assert tx.fulfillments[0].to_dict()['fulfillment'] == \
        expected.fulfillment.serialize_uri()
    assert tx.fulfillments_valid() is True

    validate_transaction_model(tx)


def test_multiple_fulfillment_validation_of_transfer_tx(user_ffill, user_cond,
                                                        user_priv, user2_pub,
                                                        user2_priv, user3_pub,
                                                        user3_priv):
    from copy import deepcopy
    from bigchaindb.common.transaction import (Transaction, TransactionLink,
                                               Fulfillment, Condition, Asset)
    from cryptoconditions import Ed25519Fulfillment
    from .util import validate_transaction_model

    tx = Transaction(Transaction.CREATE, Asset(),
                     [user_ffill, deepcopy(user_ffill)],
                     [user_cond, deepcopy(user_cond)])
    tx.sign([user_priv])

    fulfillments = [Fulfillment(cond.fulfillment, cond.owners_after,
                                TransactionLink(tx.id, index))
                    for index, cond in enumerate(tx.conditions)]
    conditions = [Condition(Ed25519Fulfillment(public_key=user3_pub),
                            [user3_pub]),
                  Condition(Ed25519Fulfillment(public_key=user3_pub),
                            [user3_pub])]
    transfer_tx = Transaction('TRANSFER', tx.asset, fulfillments, conditions)
    transfer_tx = transfer_tx.sign([user_priv])

    assert transfer_tx.fulfillments_valid(tx.conditions) is True

    validate_transaction_model(tx)


def test_validate_fulfillments_of_transfer_tx_with_invalid_params(transfer_tx,
                                                                  cond_uri,
                                                                  utx,
                                                                  user2_pub,
                                                                  user_priv):
    from bigchaindb.common.transaction import Condition
    from cryptoconditions import Ed25519Fulfillment

    invalid_cond = Condition(Ed25519Fulfillment.from_uri('cf:0:'), ['invalid'])
    assert transfer_tx.fulfillments_valid([invalid_cond]) is False
    invalid_cond = utx.conditions[0]
    invalid_cond.owners_after = 'invalid'
    assert transfer_tx.fulfillments_valid([invalid_cond]) is True

    with raises(TypeError):
        assert transfer_tx.fulfillments_valid(None) is False
    with raises(AttributeError):
        transfer_tx.fulfillments_valid('not a list')
    with raises(ValueError):
        transfer_tx.fulfillments_valid([])
    with raises(TypeError):
        transfer_tx.operation = "Operation that doesn't exist"
        transfer_tx.fulfillments_valid([utx.conditions[0]])


def test_create_create_transaction_single_io(user_cond, user_pub, data, uuid4):
    from bigchaindb.common.transaction import Transaction, Asset
    from .util import validate_transaction_model

    expected = {
        'conditions': [user_cond.to_dict()],
        'metadata': data,
        'asset': {
            'id': uuid4,
            'data': data,
        },
        'fulfillments': [
            {
                'owners_before': [
                    user_pub
                ],
                'fulfillment': None,
                'input': None
            }
        ],
        'operation': 'CREATE',
        'version': 1,
    }

    asset = Asset(data, uuid4)
    tx = Transaction.create([user_pub], [([user_pub], 1)], data, asset)
    tx_dict = tx.to_dict()
    tx_dict['fulfillments'][0]['fulfillment'] = None
    tx_dict.pop('id')

    assert tx_dict == expected

    validate_transaction_model(tx)


def test_validate_single_io_create_transaction(user_pub, user_priv, data):
    from bigchaindb.common.transaction import Transaction, Asset

    tx = Transaction.create([user_pub], [([user_pub], 1)], data, Asset())
    tx = tx.sign([user_priv])
    assert tx.fulfillments_valid() is True


def test_create_create_transaction_multiple_io(user_cond, user2_cond, user_pub,
                                               user2_pub):
    from bigchaindb.common.transaction import Transaction, Asset, Fulfillment

    # a fulfillment for a create transaction with multiple `owners_before`
    # is a fulfillment for an implicit threshold condition with
    # weight = len(owners_before)
    ffill = Fulfillment.generate([user_pub, user2_pub]).to_dict()
    expected = {
        'conditions': [user_cond.to_dict(), user2_cond.to_dict()],
        'metadata': {
            'message': 'hello'
        },
        'fulfillments': [ffill],
        'operation': 'CREATE',
        'version': 1
    }
    asset = Asset()
    tx = Transaction.create([user_pub, user2_pub],
                            [([user_pub], 1), ([user2_pub], 1)],
                            asset=asset,
                            metadata={'message': 'hello'}).to_dict()
    tx.pop('id')
    tx.pop('asset')

    assert tx == expected


def test_validate_multiple_io_create_transaction(user_pub, user_priv,
                                                 user2_pub, user2_priv):
    from bigchaindb.common.transaction import Transaction, Asset
    from .util import validate_transaction_model

    tx = Transaction.create([user_pub, user2_pub],
                            [([user_pub], 1), ([user2_pub], 1)],
                            metadata={'message': 'hello'},
                            asset=Asset())
    tx = tx.sign([user_priv, user2_priv])
    assert tx.fulfillments_valid() is True

    validate_transaction_model(tx)


def test_create_create_transaction_threshold(user_pub, user2_pub, user3_pub,
                                             user_user2_threshold_cond,
                                             user_user2_threshold_ffill, data,
                                             uuid4):
    from bigchaindb.common.transaction import Transaction, Asset

    expected = {
        'conditions': [user_user2_threshold_cond.to_dict()],
        'metadata': data,
        'asset': {
            'id': uuid4,
            'data': data,
        },
        'fulfillments': [
            {
                'owners_before': [
                    user_pub,
                ],
                'fulfillment': None,
                'input': None
            },
        ],
        'operation': 'CREATE',
        'version': 1
    }
    asset = Asset(data, uuid4)
    tx = Transaction.create([user_pub], [([user_pub, user2_pub], 1)],
                            data, asset)
    tx_dict = tx.to_dict()
    tx_dict.pop('id')
    tx_dict['fulfillments'][0]['fulfillment'] = None

    assert tx_dict == expected


def test_validate_threshold_create_transaction(user_pub, user_priv, user2_pub,
                                               data):
    from bigchaindb.common.transaction import Transaction, Asset
    from .util import validate_transaction_model

    tx = Transaction.create([user_pub], [([user_pub, user2_pub], 1)],
                            data, Asset())
    tx = tx.sign([user_priv])
    assert tx.fulfillments_valid() is True

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


def test_conditions_to_inputs(tx):
    ffills = tx.to_inputs([0])
    assert len(ffills) == 1
    ffill = ffills.pop()
    assert ffill.fulfillment == tx.conditions[0].fulfillment
    assert ffill.owners_before == tx.conditions[0].owners_after
    assert ffill.tx_input.txid == tx.id
    assert ffill.tx_input.cid == 0


def test_create_transfer_transaction_single_io(tx, user_pub, user2_pub,
                                               user2_cond, user_priv, uuid4):
    from copy import deepcopy
    from bigchaindb.common.crypto import PrivateKey
    from bigchaindb.common.transaction import Transaction, Asset
    from bigchaindb.common.util import serialize
    from .util import validate_transaction_model

    expected = {
        'conditions': [user2_cond.to_dict()],
        'metadata': None,
        'asset': {
            'id': uuid4,
        },
        'fulfillments': [
            {
                'owners_before': [
                    user_pub
                ],
                'fulfillment': None,
                'input': {
                    'txid': tx.id,
                    'cid': 0
                }
            }
        ],
        'operation': 'TRANSFER',
        'version': 1
    }
    inputs = tx.to_inputs([0])
    asset = Asset(None, uuid4)
    transfer_tx = Transaction.transfer(inputs, [([user2_pub], 1)], asset=asset)
    transfer_tx = transfer_tx.sign([user_priv])
    transfer_tx = transfer_tx.to_dict()

    expected_input = deepcopy(inputs[0])
    expected['id'] = transfer_tx['id']
    expected_input.fulfillment.sign(serialize(expected).encode(),
                                    PrivateKey(user_priv))
    expected_ffill = expected_input.fulfillment.serialize_uri()
    transfer_ffill = transfer_tx['fulfillments'][0]['fulfillment']

    assert transfer_ffill == expected_ffill

    transfer_tx = Transaction.from_dict(transfer_tx)
    assert transfer_tx.fulfillments_valid([tx.conditions[0]]) is True

    validate_transaction_model(transfer_tx)


def test_create_transfer_transaction_multiple_io(user_pub, user_priv,
                                                 user2_pub, user2_priv,
                                                 user3_pub, user2_cond):
    from bigchaindb.common.transaction import Transaction, Asset

    asset = Asset()
    tx = Transaction.create([user_pub], [([user_pub], 1), ([user2_pub], 1)],
                            asset=asset, metadata={'message': 'hello'})
    tx = tx.sign([user_priv])

    expected = {
        'conditions': [user2_cond.to_dict(), user2_cond.to_dict()],
        'metadata': None,
        'fulfillments': [
            {
                'owners_before': [
                    user_pub
                ],
                'fulfillment': None,
                'input': {
                    'txid': tx.id,
                    'cid': 0
                }
            }, {
                'owners_before': [
                    user2_pub
                ],
                'fulfillment': None,
                'input': {
                    'txid': tx.id,
                    'cid': 1
                }
            }
        ],
        'operation': 'TRANSFER',
        'version': 1
    }

    transfer_tx = Transaction.transfer(tx.to_inputs(),
                                       [([user2_pub], 1), ([user2_pub], 1)],
                                       asset=tx.asset)
    transfer_tx = transfer_tx.sign([user_priv, user2_priv])

    assert len(transfer_tx.fulfillments) == 2
    assert len(transfer_tx.conditions) == 2

    assert transfer_tx.fulfillments_valid(tx.conditions) is True

    transfer_tx = transfer_tx.to_dict()
    transfer_tx['fulfillments'][0]['fulfillment'] = None
    transfer_tx['fulfillments'][1]['fulfillment'] = None
    transfer_tx.pop('asset')
    transfer_tx.pop('id')

    assert expected == transfer_tx


def test_create_transfer_with_invalid_parameters(user_pub):
    from bigchaindb.common.transaction import Transaction, Asset

    with raises(TypeError):
        Transaction.transfer({}, [], Asset())
    with raises(ValueError):
        Transaction.transfer([], [], Asset())
    with raises(TypeError):
        Transaction.transfer(['fulfillment'], {}, Asset())
    with raises(ValueError):
        Transaction.transfer(['fulfillment'], [], Asset())
    with raises(ValueError):
        Transaction.transfer(['fulfillment'], [user_pub], Asset())
    with raises(ValueError):
        Transaction.transfer(['fulfillment'], [([user_pub],)], Asset())


def test_cant_add_empty_condition():
    from bigchaindb.common.transaction import Transaction, Asset

    with patch.object(Asset, 'validate_asset', return_value=None):
        tx = Transaction(Transaction.CREATE, None)
    with raises(TypeError):
        tx.add_condition(None)


def test_cant_add_empty_fulfillment():
    from bigchaindb.common.transaction import Transaction, Asset

    with patch.object(Asset, 'validate_asset', return_value=None):
        tx = Transaction(Transaction.CREATE, None)
    with raises(TypeError):
        tx.add_fulfillment(None)
