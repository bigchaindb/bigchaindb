from pytest import raises


def test_fulfillment_serialization(ffill_uri, user_pub):
    from bigchaindb_common.transaction import Fulfillment
    from cryptoconditions import Fulfillment as CCFulfillment

    expected = {
        'owners_before': [user_pub],
        'fulfillment': ffill_uri,
        'details': CCFulfillment.from_uri(ffill_uri).to_dict(),
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
        'details': CCFulfillment.from_uri(ffill_uri).to_dict(),
        'input': None,
    }
    ffill = Fulfillment.from_dict(ffill)

    assert ffill == expected


def test_fulfillment_deserialization_with_dict(cc_ffill, user_pub):
    from bigchaindb_common.transaction import Fulfillment

    expected = Fulfillment(cc_ffill, [user_pub])

    ffill = {
        'owners_before': [user_pub],
        'fulfillment': None,
        'details': cc_ffill.to_dict(),
        'input': None,
    }
    ffill = Fulfillment.from_dict(ffill)

    assert ffill == expected


def test_invalid_fulfillment_initialization(cc_ffill, user_pub):
    from bigchaindb_common.transaction import Fulfillment

    with raises(TypeError):
        Fulfillment(cc_ffill, user_pub)
    with raises(TypeError):
        Fulfillment(cc_ffill, [], tx_input='somethingthatiswrong')


def test_gen_default_fulfillment_with_single_owner_after(user_pub):
    from bigchaindb_common.transaction import Fulfillment
    from cryptoconditions import Ed25519Fulfillment

    ffill = Fulfillment.gen_default([user_pub])
    assert ffill.owners_before == [user_pub]
    assert ffill.tx_input is None
    assert ffill.fulfillment.to_dict() == Ed25519Fulfillment(public_key=user_pub).to_dict()


def test_gen_default_fulfillment_with_multiple_owners_after(user_pub_keys):
    from bigchaindb_common.transaction import Fulfillment
    from cryptoconditions import Ed25519Fulfillment, ThresholdSha256Fulfillment

    ffill = Fulfillment.gen_default(user_pub_keys)
    expected_ffill = ThresholdSha256Fulfillment(threshold=len(user_pub_keys))
    # NOTE: Does it make sense to have the exact same logic as in the tested method here?
    for user_pub in user_pub_keys:
        expected_ffill.add_subfulfillment(Ed25519Fulfillment(public_key=user_pub))

    assert ffill.owners_before == user_pub_keys
    assert ffill.tx_input is None
    assert ffill.fulfillment.to_dict() == expected_ffill.to_dict()


def test_invalid_gen_default_arguments():
    from bigchaindb_common.transaction import Fulfillment

    with raises(TypeError):
        Fulfillment.gen_default({})
    with raises(NotImplementedError):
        Fulfillment.gen_default([])


def test_condition_serialization(cond_uri, user_pub):
    from bigchaindb_common.transaction import Condition

    expected = {
        'condition': cond_uri,
        'owners_after': [user_pub],
    }

    cond = Condition(cond_uri, [user_pub])

    assert cond.to_dict() == expected


def test_condition_deserialization(cond_uri, user_pub):
    from bigchaindb_common.transaction import Condition

    expected = Condition(cond_uri, [user_pub])
    cond = {
        'condition': cond_uri,
        'owners_after': [user_pub],
    }
    cond = Condition.from_dict(cond)

    assert cond == expected


def test_invalid_condition_initialization(cond_uri, user_pub):
    from bigchaindb_common.transaction import Condition

    with raises(TypeError):
        Condition(cond_uri, user_pub)


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


def test_transaction_serialization(default_single_ffill, default_single_cond):
    from bigchaindb_common.transaction import Transaction

    tx_id = 'l0l'
    timestamp = '66666666666'

    expected = {
        'id': tx_id,
        'version': Transaction.VERSION,
        'transaction': {
            # NOTE: This test assumes that Fulfillments and Conditions can successfully be serialized
            'fulfillments': [default_single_ffill.to_dict()],
            'conditions': [default_single_cond.to_dict()],
            'operation': Transaction.CREATE,
            'timestamp': timestamp,
            'data': None,
        }
    }

    tx_dict = Transaction(Transaction.CREATE, [default_single_ffill], [default_single_cond]).to_dict()
    tx_dict['id'] = tx_id
    tx_dict['transaction']['timestamp'] = timestamp

    assert tx_dict == expected


def test_transaction_deserialization(default_single_ffill, default_single_cond):
    from bigchaindb_common.transaction import Transaction

    timestamp = '66666666666'

    expected = Transaction(Transaction.CREATE, [default_single_ffill], [default_single_cond], None, timestamp,
                           Transaction.VERSION)

    tx = {
        'version': Transaction.VERSION,
        'transaction': {
            # NOTE: This test assumes that Fulfillments and Conditions can successfully be serialized
            'fulfillments': [default_single_ffill.to_dict()],
            'conditions': [default_single_cond.to_dict()],
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


def test_add_fulfillment_to_tx(default_single_ffill):
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE, [], [])
    tx.add_fulfillment(default_single_ffill)

    assert len(tx.fulfillments) == 1


def test_add_fulfillment_to_tx_with_invalid_parameters():
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE)
    with raises(TypeError):
        tx.add_fulfillment('somewronginput')


def test_add_condition_to_tx(default_single_cond):
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE)
    tx.add_condition(default_single_cond)

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


def test_validate_tx_simple_signature(default_single_ffill, default_single_cond, user_priv):
    from copy import deepcopy

    from bigchaindb_common.crypto import SigningKey
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE, [default_single_ffill], [default_single_cond])
    expected = deepcopy(default_single_ffill)
    expected.fulfillment.sign(str(tx), SigningKey(user_priv))
    tx.sign([user_priv])

    assert tx.fulfillments[0].fulfillment.to_dict()['signature'] == expected.fulfillment.to_dict()['signature']
    assert tx.fulfillments_valid() is True


def test_invoke_simple_signature_fulfillment_with_invalid_parameters(utx, default_single_ffill):
    from bigchaindb_common.exceptions import KeypairMismatchException

    with raises(KeypairMismatchException):
        utx._sign_simple_signature_fulfillment(default_single_ffill,
                                               'somemessage',
                                               {'wrong_pub_key': 'wrong_priv_key'})


def test_invoke_threshold_signature_fulfillment_with_invalid_parameters(utx, default_threshold_ffill, user3_pub,
                                                                        user3_priv, user_pub_keys):
    from bigchaindb_common.exceptions import KeypairMismatchException

    with raises(KeypairMismatchException):
        utx._sign_threshold_signature_fulfillment(default_threshold_ffill, 'somemessage', {user3_pub: user3_priv})
    with raises(KeypairMismatchException):
        default_threshold_ffill.owners_before = ['somewrongvalue']
        utx._sign_threshold_signature_fulfillment(default_threshold_ffill, 'somemessage', None)


def test_validate_fulfillment_with_invalid_parameters(utx):
    assert utx._fulfillment_valid() == False


def test_validating_multiple_fulfillments(default_single_ffill, default_single_cond, user_priv):
    from copy import deepcopy

    from bigchaindb_common.crypto import SigningKey
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE,
                     [default_single_ffill, deepcopy(default_single_ffill)],
                     [default_single_cond, deepcopy(default_single_cond)])

    expected_first = deepcopy(tx)
    expected_second= deepcopy(tx)
    expected_first.fulfillments = [expected_first.fulfillments[0]]
    expected_first.conditions= [expected_first.conditions[0]]
    expected_second.fulfillments = [expected_second.fulfillments[1]]
    expected_second.conditions= [expected_second.conditions[1]]

    expected_first.fulfillments[0].fulfillment.sign(str(expected_first), SigningKey(user_priv))
    expected_second.fulfillments[0].fulfillment.sign(str(expected_second), SigningKey(user_priv))
    tx.sign([user_priv])

    assert tx.fulfillments[0].fulfillment.to_dict() == expected_first.fulfillments[0].fulfillment.to_dict()
    assert tx.fulfillments[1].fulfillment.to_dict() == expected_second.fulfillments[0].fulfillment.to_dict()
    assert tx.fulfillments_valid() is True


def test_validate_tx_threshold_signature(default_threshold_ffill, default_threshold_cond, user_pub_keys,
                                         user_priv_keys):
    from copy import deepcopy

    from bigchaindb_common.crypto import SigningKey
    from bigchaindb_common.transaction import Transaction

    tx = Transaction(Transaction.CREATE, [default_threshold_ffill], [default_threshold_cond])
    expected = deepcopy(default_threshold_ffill)
    expected.fulfillment.subconditions[0]['body'].sign(str(tx), SigningKey(user_priv_keys[0]))
    expected.fulfillment.subconditions[1]['body'].sign(str(tx), SigningKey(user_priv_keys[1]))
    tx.sign(user_priv_keys)

    assert tx.fulfillments[0].to_dict()['fulfillment'] == expected.to_dict()['fulfillment']
    assert tx.fulfillments_valid() is True


def test_transfer(utx, user_pub, user_priv, user2_pub, cond_uri):
    from copy import deepcopy

    from bigchaindb_common.crypto import SigningKey
    from bigchaindb_common.transaction import Condition
    from cryptoconditions import Ed25519Fulfillment

    cond = Condition(Ed25519Fulfillment(public_key=user2_pub).condition_uri, [user2_pub])
    transfer_tx = utx.transfer([cond])

    expected = deepcopy(transfer_tx.fulfillments[0])
    expected.fulfillment.sign(str(transfer_tx), SigningKey(user_priv))

    transfer_tx.sign([user_priv])

    assert utx.fulfillments[0].fulfillment.to_dict()['signature'] == expected.fulfillment.to_dict()['signature']
    assert transfer_tx.fulfillments_valid(utx.conditions) is True


def test_multiple_fulfillment_validation_of_transfer_tx(default_single_ffill, default_single_cond, user_priv,
                                                        user2_pub, user2_priv, user3_pub, user3_priv):
    from copy import deepcopy

    from bigchaindb_common.transaction import Transaction, Condition
    from cryptoconditions import Ed25519Fulfillment

    tx = Transaction(Transaction.CREATE,
                     [default_single_ffill, deepcopy(default_single_ffill)],
                     [default_single_cond, deepcopy(default_single_cond)])
    tx.sign([user_priv])
    conditions = [Condition(Ed25519Fulfillment(public_key=user2_pub).condition_uri, [user2_pub]),
                  Condition(Ed25519Fulfillment(public_key=user3_pub).condition_uri, [user3_pub])]
    transfer_utx = tx.transfer(conditions)
    transfer_tx = transfer_utx.sign([user_priv])

    assert transfer_tx.fulfillments_valid(tx.conditions) is True


def test_validate_fulfillments_of_transfer_tx_with_invalid_parameters(transfer_tx,
                                                                      cond_uri,
                                                                      utx,
                                                                      user2_pub,
                                                                      user_priv):
    from bigchaindb_common.transaction import Condition

    assert transfer_tx.fulfillments_valid([Condition('invalidly formed condition uri',
                                                     ['invalid'])]) is False
    assert transfer_tx.fulfillments_valid([Condition(cond_uri, [user2_pub])]) is False

    with raises(ValueError):
        assert transfer_tx.fulfillments_valid(None) is False
    with raises(TypeError):
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
