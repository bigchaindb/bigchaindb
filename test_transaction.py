from pytest import raises


def test_fulfillment_serialization(ffill_uri, user_pub):
    from bigchaindb_common.transaction import Fulfillment
    from cryptoconditions import Fulfillment as CCFulfillment

    expected = {
        'owners_before': [user_pub],
        'fulfillment': ffill_uri,
        'input': None,
    }
    ffill = Fulfillment(CCFulfillment.from_uri(ffill_uri), [user_pub])
    assert ffill.to_dict() == expected


def test_fulfillment_deserialization_with_uri(ffill_uri, user_pub):
    from bigchaindb_common.transaction import Fulfillment
    from cryptoconditions import Fulfillment as CCFulfillment

    expected = Fulfillment(CCFulfillment.from_uri(ffill_uri), [user_pub])
    ffill = {
        'owners_before': [user_pub],
        'fulfillment': ffill_uri,
        'input': None,
    }
    ffill = Fulfillment.from_dict(ffill)

    assert ffill == expected


def test_fulfillment_deserialization_with_dict(user_pub):
    from bigchaindb_common.transaction import Fulfillment

    expected = Fulfillment(None, [user_pub])

    ffill = {
        'owners_before': [user_pub],
        'fulfillment': None,
        'input': None,
    }
    ffill = Fulfillment.from_dict(ffill)

    assert ffill == expected


def test_condition_serialization(user_Ed25519, user_pub):
    from bigchaindb_common.transaction import Condition

    expected = {
        'condition': {
            'uri': user_Ed25519.condition_uri,
            'details': user_Ed25519.to_dict(),
        },
        'owners_after': [user_pub],
    }

    cond = Condition(user_Ed25519, [user_pub])

    assert cond.to_dict() == expected


def test_condition_deserialization(user_Ed25519, user_pub):
    from bigchaindb_common.transaction import Condition

    expected = Condition(user_Ed25519, [user_pub])
    cond = {
        'condition': {
            'uri': user_Ed25519.condition_uri,
            'details': user_Ed25519.to_dict()
        },
        'owners_after': [user_pub],
    }
    cond = Condition.from_dict(cond)

    assert cond == expected


def test_invalid_condition_initialization(cond_uri, user_pub):
    from bigchaindb_common.transaction import Condition

    with raises(TypeError):
        Condition(cond_uri, user_pub)


def test_transaction_serialization(user_ffill, user_cond):
    from bigchaindb_common.transaction import Transaction

    tx_id = 'l0l'
    timestamp = '66666666666'

    expected = {
        'id': tx_id,
        'version': Transaction.VERSION,
        'transaction': {
            # NOTE: This test assumes that Fulfillments and Conditions can successfully be serialized
            'fulfillments': [user_ffill.to_dict(0)],
            'conditions': [user_cond.to_dict(0)],
            'operation': Transaction.CREATE,
            'timestamp': timestamp,
            'data': None,
        }
    }

    tx_dict = Transaction(Transaction.CREATE, [user_ffill], [user_cond]).to_dict()
    tx_dict['id'] = tx_id
    tx_dict['transaction']['timestamp'] = timestamp

    assert tx_dict == expected


def test_transaction_deserialization(user_ffill, user_cond):
    from bigchaindb_common.transaction import Transaction

    timestamp = '66666666666'

    expected = Transaction(Transaction.CREATE, [user_ffill], [user_cond], None, timestamp,
                           Transaction.VERSION)

    tx = {
        'version': Transaction.VERSION,
        'transaction': {
            # NOTE: This test assumes that Fulfillments and Conditions can successfully be serialized
            'fulfillments': [user_ffill.to_dict()],
            'conditions': [user_cond.to_dict()],
            'operation': Transaction.CREATE,
            'timestamp': timestamp,
            'data': None,
        }
    }
    tx['id'] = Transaction._to_hash(Transaction._to_str(Transaction._remove_signatures(tx)))
    tx = Transaction.from_dict(tx)

    assert tx == expected


def test_tx_serialization_with_incorrect_hash(utx):
    from bigchaindb_common.transaction import Transaction
    from bigchaindb_common.exceptions import InvalidHash

    utx_dict = utx.to_dict()
    utx_dict['id'] = 'abc'
    with raises(InvalidHash):
        Transaction.from_dict(utx_dict)
    utx_dict.pop('id')
    with raises(InvalidHash):
        Transaction.from_dict(utx_dict)
    utx_dict['id'] = []
    with raises(InvalidHash):
        Transaction.from_dict(utx_dict)


def test_invalid_tx_initialization():
    from bigchaindb_common.transaction import Transaction

    wrong_data_type = {'payload': 'a totally wrong datatype'}
    with raises(TypeError):
        Transaction(Transaction.CREATE, wrong_data_type)
    with raises(TypeError):
        Transaction(Transaction.CREATE, [], wrong_data_type)
    with raises(TypeError):
        Transaction(Transaction.CREATE, [], [], wrong_data_type)
    with raises(TypeError):
        Transaction('RANSFER', [], [])


def test_invalid_fulfillment_initialization(user_ffill, user_pub):
    from bigchaindb_common.transaction import Fulfillment

    with raises(TypeError):
        Fulfillment(user_ffill, user_pub)
    with raises(TypeError):
        Fulfillment(user_ffill, [], tx_input='somethingthatiswrong')


def test_invalid_data_initialization():
    from bigchaindb_common.transaction import Data

    with raises(TypeError):
        Data([])


def test_data_serialization(payload, payload_id):
    from bigchaindb_common.transaction import Data

    expected = {
        'payload': payload,
        'uuid': payload_id
    }
    data = Data(payload, payload_id)

    assert data.to_dict() == expected


def test_data_deserialization(payload, payload_id):
    from bigchaindb_common.transaction import Data

    expected = Data(payload, payload_id)
    data = Data.from_dict({'payload': payload, 'uuid': payload_id})

    assert data == expected


def test_transaction_link_serialization():
    from bigchaindb_common.transaction import TransactionLink

    tx_id = 'a transaction id'
    expected = {
        'txid': tx_id,
        'cid': 0,
    }
    tx_link = TransactionLink(tx_id, 0)

    assert tx_link.to_dict() == expected


def test_transaction_link_serialization_with_empty_payload():
    from bigchaindb_common.transaction import TransactionLink

    expected = None
    tx_link = TransactionLink()

    assert tx_link.to_dict() == expected


def test_transaction_link_deserialization():
    from bigchaindb_common.transaction import TransactionLink

    tx_id = 'a transaction id'
    expected = TransactionLink(tx_id, 0)
    tx_link = {
        'txid': tx_id,
        'cid': 0,
    }
    tx_link = TransactionLink.from_dict(tx_link)

    assert tx_link == expected


def test_transaction_link_deserialization_with_empty_payload():
    from bigchaindb_common.transaction import TransactionLink

    expected = TransactionLink()
    tx_link = TransactionLink.from_dict(None)

    assert tx_link == expected


def test_add_fulfillment_to_tx(user_ffill):
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE, [], [])
    tx.add_fulfillment(user_ffill)

    assert len(tx.fulfillments) == 1


def test_add_fulfillment_to_tx_with_invalid_parameters():
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE)
    with raises(TypeError):
        tx.add_fulfillment('somewronginput')


def test_add_condition_to_tx(user_cond):
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE)
    tx.add_condition(user_cond)

    assert len(tx.conditions) == 1


def test_add_condition_to_tx_with_invalid_parameters():
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE, [], [])
    with raises(TypeError):
        tx.add_condition('somewronginput')


def test_sign_with_invalid_parameters(utx, user_priv):
    with raises(TypeError):
        utx.sign(None)
    with raises(TypeError):
        utx.sign(user_priv)


def test_validate_tx_simple_create_signature(user_ffill, user_cond, user_priv):
    from copy import deepcopy
    from bigchaindb_common.crypto import SigningKey
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE, [user_ffill], [user_cond])
    expected = deepcopy(user_cond)
    expected.fulfillment.sign(str(tx), SigningKey(user_priv))
    tx.sign([user_priv])

    assert tx.fulfillments[0].to_dict()['fulfillment'] == expected.fulfillment.serialize_uri()
    assert tx.fulfillments_valid() is True


def test_invoke_simple_signature_fulfillment_with_invalid_parameters(utx, user_ffill):
    from bigchaindb_common.exceptions import KeypairMismatchException

    with raises(KeypairMismatchException):
        utx._sign_simple_signature_fulfillment(user_ffill,
                                               0,
                                               'somemessage',
                                               {'wrong_pub_key': 'wrong_priv_key'})


def test_invoke_threshold_signature_fulfillment_with_invalid_parameters(utx,
                                                                        user_user2_threshold_ffill,
                                                                        user3_pub,
                                                                        user3_priv):
    from bigchaindb_common.exceptions import KeypairMismatchException

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
    from bigchaindb_common.transaction import Transaction
    input_conditions = [cond.fulfillment.condition_uri for cond
                        in utx.conditions]
    tx_serialized = Transaction._to_str(Transaction._remove_signatures(utx.to_dict()))
    assert utx._fulfillment_valid(utx.fulfillments[0],
                                  tx_serialized,
                                  input_conditions) == False


def test_validate_multiple_fulfillments(user_ffill, user_cond, user_priv):
    from copy import deepcopy

    from bigchaindb_common.crypto import SigningKey
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE,
                     [user_ffill, deepcopy(user_ffill)],
                     [user_ffill, deepcopy(user_cond)])

    expected_first = deepcopy(tx)
    expected_second = deepcopy(tx)
    expected_first.fulfillments = [expected_first.fulfillments[0]]
    expected_first.conditions = [expected_first.conditions[0]]
    expected_second.fulfillments = [expected_second.fulfillments[1]]
    expected_second.conditions = [expected_second.conditions[1]]

    expected_first.fulfillments[0].fulfillment.sign(str(expected_first), SigningKey(user_priv))
    expected_second.fulfillments[0].fulfillment.sign(str(expected_second), SigningKey(user_priv))
    tx.sign([user_priv])

    assert tx.fulfillments[0].to_dict()['fulfillment'] == expected_first.fulfillments[0].fulfillment.serialize_uri()
    assert tx.fulfillments[1].to_dict()['fulfillment'] == expected_second.fulfillments[0].fulfillment.serialize_uri()
    assert tx.fulfillments_valid() is True


def test_validate_tx_threshold_create_signature(user_user2_threshold_ffill,
                                                user_user2_threshold_cond,
                                                user_pub,
                                                user2_pub,
                                                user_priv,
                                                user2_priv):
    from copy import deepcopy

    from bigchaindb_common.crypto import SigningKey
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE, [user_user2_threshold_ffill], [user_user2_threshold_cond])
    expected = deepcopy(user_user2_threshold_cond)
    expected.fulfillment.subconditions[0]['body'].sign(str(tx), SigningKey(user_priv))
    expected.fulfillment.subconditions[1]['body'].sign(str(tx), SigningKey(user2_priv))
    tx.sign([user_priv, user2_priv])

    assert tx.fulfillments[0].to_dict()['fulfillment'] == expected.fulfillment.serialize_uri()
    assert tx.fulfillments_valid() is True


def test_multiple_fulfillment_validation_of_transfer_tx(user_ffill, user_cond,
                                                        user_priv, user2_pub,
                                                        user2_priv, user3_pub,
                                                        user3_priv):
    from copy import deepcopy
    from bigchaindb_common.transaction import (Transaction, TransactionLink,
                                               Fulfillment, Condition)
    from cryptoconditions import Ed25519Fulfillment

    tx = Transaction(Transaction.CREATE,
                     [user_ffill, deepcopy(user_ffill)],
                     [user_cond, deepcopy(user_cond)])
    tx.sign([user_priv])

    fulfillments = [Fulfillment(cond.fulfillment, cond.owners_after,
                                TransactionLink(tx.id, index))
                    for index, cond in enumerate(tx.conditions)]
    conditions = [Condition(Ed25519Fulfillment(public_key=user3_pub), [user3_pub]),
                  Condition(Ed25519Fulfillment(public_key=user3_pub), [user3_pub])]
    transfer_tx = Transaction('TRANSFER', fulfillments, conditions)

    transfer_tx = transfer_tx.sign([user_priv])

    assert transfer_tx.fulfillments_valid(tx.conditions) is True


def test_validate_fulfillments_of_transfer_tx_with_invalid_parameters(transfer_tx,
                                                                      cond_uri,
                                                                      utx,
                                                                      user2_pub,
                                                                      user_priv):
    from bigchaindb_common.transaction import Condition
    from cryptoconditions import Ed25519Fulfillment

    assert transfer_tx.fulfillments_valid([Condition(Ed25519Fulfillment.from_uri('cf:0:'),
                                                     ['invalid'])]) is False
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
    with raises(ValueError):
        tx = utx.sign([user_priv])
        tx.conditions = []
        tx.fulfillments_valid()


def test_create_create_transaction_single_io(user_cond, user_pub):
    from bigchaindb_common.transaction import Transaction

    expected = {
        'transaction': {
            'conditions': [user_cond.to_dict(0)],
            'data': {
                'payload': {
                    'message': 'hello'
                }
            },
            'fulfillments': [
                {
                    'owners_before': [
                        user_pub
                    ],
                    'fid': 0,
                    'fulfillment': None,
                    'input': None
                }
            ],
            'operation': 'CREATE',
        },
        'version': 1
    }

    tx = Transaction.create([user_pub], [user_pub], {'message': 'hello'}).to_dict()
    # TODO: Fix this with monkeypatching
    tx.pop('id')
    tx['transaction']['data'].pop('uuid')
    tx['transaction'].pop('timestamp')

    assert tx == expected


def test_validate_single_io_create_transaction(user_pub, user_priv):
    from bigchaindb_common.transaction import Transaction

    tx = Transaction.create([user_pub], [user_pub], {'message': 'hello'})
    tx = tx.sign([user_priv])
    assert tx.fulfillments_valid() is True


def test_create_create_transaction_multiple_io(user_cond, user2_cond, user_pub,
                                               user2_pub):
    from bigchaindb_common.transaction import Transaction

    expected = {
        'transaction': {
            'conditions': [user_cond.to_dict(0), user2_cond.to_dict(1)],
            'data': {
                'payload': {
                    'message': 'hello'
                }
            },
            'fulfillments': [
                {
                    'owners_before': [
                        user_pub,
                    ],
                    'fid': 0,
                    'fulfillment': None,
                    'input': None
                },
                {
                    'owners_before': [
                        user2_pub,
                    ],
                    'fid': 1,
                    'fulfillment': None,
                    'input': None
                }
            ],
            'operation': 'CREATE',
        },
        'version': 1
    }
    tx = Transaction.create([user_pub, user2_pub], [user_pub, user2_pub],
                            {'message': 'hello'}).to_dict()
    # TODO: Fix this with monkeypatching
    tx.pop('id')
    tx['transaction']['data'].pop('uuid')
    tx['transaction'].pop('timestamp')

    assert tx == expected


def test_validate_multiple_io_create_transaction(user_pub, user_priv,
                                                 user2_pub, user2_priv):
    from bigchaindb_common.transaction import Transaction

    tx = Transaction.create([user_pub, user2_pub], [user_pub, user2_pub],
                            {'message': 'hello'})
    tx = tx.sign([user_priv, user2_priv])
    assert tx.fulfillments_valid() is True


def test_create_create_transaction_threshold(user_pub, user2_pub, user3_pub,
                                             user_user2_threshold_cond,
                                             user_user2_threshold_ffill):
    from bigchaindb_common.transaction import Transaction

    expected = {
        'transaction': {
            'conditions': [user_user2_threshold_cond.to_dict(0)],
            'data': {
                'payload': {
                    'message': 'hello'
                }
            },
            'fulfillments': [
                {
                    'owners_before': [
                        user_pub,
                    ],
                    'fid': 0,
                    'fulfillment': None,
                    'input': None
                },
            ],
            'operation': 'CREATE',
        },
        'version': 1
    }
    tx = Transaction.create([user_pub], [user_pub, user2_pub],
                            {'message': 'hello'}).to_dict()
    # TODO: Fix this with monkeypatching
    tx.pop('id')
    tx['transaction']['data'].pop('uuid')
    tx['transaction'].pop('timestamp')

    assert tx == expected


def test_validate_threshold_create_transaction(user_pub, user_priv, user2_pub):
    from bigchaindb_common.transaction import Transaction

    tx = Transaction.create([user_pub], [user_pub, user2_pub],
                            {'message': 'hello'})
    tx = tx.sign([user_priv])
    assert tx.fulfillments_valid() is True


def test_create_create_transaction_hashlock(user_pub):
    from bigchaindb_common.transaction import Transaction, Condition
    from cryptoconditions import PreimageSha256Fulfillment

    secret = b'much secret, wow'
    hashlock = PreimageSha256Fulfillment(preimage=secret)
    cond = Condition(hashlock)

    expected = {
        'transaction': {
            'conditions': [cond.to_dict(0)],
            'data': {
                'payload': {
                    'message': 'hello'
                }
            },
            'fulfillments': [
                {
                    'owners_before': [
                        user_pub,
                    ],
                    'fid': 0,
                    'fulfillment': None,
                    'input': None
                },
            ],
            'operation': 'CREATE',
        },
        'version': 1
    }

    tx = Transaction.create([user_pub], [], {'message': 'hello'},
                            secret).to_dict()
    # TODO: Fix this with monkeypatching
    tx.pop('id')
    tx['transaction']['data'].pop('uuid')
    tx['transaction'].pop('timestamp')

    assert tx == expected


def test_validate_hashlock_create_transaction(user_pub, user_priv):
    from bigchaindb_common.transaction import Transaction

    tx = Transaction.create([user_pub], [], {'message': 'hello'},
                            b'much secret, wow')
    tx = tx.sign([user_priv])
    assert tx.fulfillments_valid() is True
