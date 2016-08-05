from pytest import raises


def test_fulfillment_serialization(ffill_uri, user_vk):
    from bigchaindb.transaction import Fulfillment
    from cryptoconditions import Fulfillment as CCFulfillment

    expected = {
        'owners_before': [user_vk],
        'fulfillment': ffill_uri,
        'details': CCFulfillment.from_uri(ffill_uri).to_dict(),
        'fid': 0,
        'input': None,
    }
    ffill = Fulfillment(CCFulfillment.from_uri(ffill_uri), [user_vk])

    assert ffill.to_dict() == expected


def test_fulfillment_deserialization_with_uri(ffill_uri, user_vk):
    from bigchaindb.transaction import Fulfillment
    from cryptoconditions import Fulfillment as CCFulfillment

    expected = Fulfillment(CCFulfillment.from_uri(ffill_uri), [user_vk])
    ffill = {
        'owners_before': [user_vk],
        'fulfillment': ffill_uri,
        'details': CCFulfillment.from_uri(ffill_uri).to_dict(),
        'fid': 0,
        'input': None,
    }
    ffill = Fulfillment.from_dict(ffill)

    assert ffill.to_dict() == expected.to_dict()


def test_fulfillment_deserialization_with_dict(cc_ffill, user_vk):
    from bigchaindb.transaction import Fulfillment

    expected = Fulfillment(cc_ffill, [user_vk])

    ffill = {
        'owners_before': [user_vk],
        'fulfillment': None,
        'details': cc_ffill.to_dict(),
        'fid': 0,
        'input': None,
    }
    ffill = Fulfillment.from_dict(ffill)

    assert ffill.to_dict() == expected.to_dict()


def test_invalid_fulfillment_initialization(cc_ffill, user_vk):
    from bigchaindb.transaction import Fulfillment

    with raises(TypeError):
        Fulfillment(cc_ffill, user_vk)


def test_gen_default_fulfillment(user_vk):
    from bigchaindb.transaction import Fulfillment
    from cryptoconditions import Ed25519Fulfillment

    ffill = Fulfillment.gen_default(user_vk)
    assert ffill.owners_before == [user_vk]
    assert ffill.fid == 0
    assert ffill.fulfillment.to_dict() == Ed25519Fulfillment(public_key=user_vk).to_dict()
    assert ffill.tx_input is None


def test_condition_serialization(cond_uri, user_vk):
    from bigchaindb.transaction import Condition

    expected = {
        'condition': cond_uri,
        'owners_after': [user_vk],
        'cid': 0,
    }

    cond = Condition(cond_uri, [user_vk])

    assert cond.to_dict() == expected


def test_condition_deserialization(cond_uri, user_vk):
    from bigchaindb.transaction import Condition

    expected = Condition(cond_uri, [user_vk])
    cond = {
        'condition': cond_uri,
        'owners_after': [user_vk],
        'cid': 0,
    }
    cond = Condition.from_dict(cond)

    assert cond.to_dict() == expected.to_dict()


def test_invalid_condition_initialization(cond_uri, user_vk):
    from bigchaindb.transaction import Condition

    with raises(TypeError):
        Condition(cond_uri, user_vk)


def test_invalid_data_initialization():
    from bigchaindb.transaction import Data

    with raises(TypeError):
        Data([])


def test_data_serialization(payload, payload_id):
    from bigchaindb.transaction import Data

    expected = {
        'payload': payload,
        'hash': payload_id
    }
    data = Data(payload, payload_id)

    assert data.to_dict() == expected


def test_data_deserialization(payload, payload_id):
    from bigchaindb.transaction import Data

    expected = Data(payload, payload_id)
    data = Data.from_dict({'payload': payload, 'hash': payload_id})

    assert data.to_dict() == expected.to_dict()


def test_transaction_serialization(default_ffill, default_cond):
    from bigchaindb.transaction import Transaction

    tx_id = 'l0l'
    timestamp = '66666666666'

    expected = {
        'id': tx_id,
        'version': Transaction.VERSION,
        'transaction': {
            # NOTE: This test assumes that Fulfillments and Conditions can successfully be serialized
            'fulfillments': [default_ffill.to_dict()],
            'conditions': [default_cond.to_dict()],
            'operation': Transaction.CREATE,
            'timestamp': timestamp,
            'data': None,
        }
    }

    tx_dict = Transaction(Transaction.CREATE, [default_ffill], [default_cond]).to_dict()
    tx_dict['id'] = tx_id
    tx_dict['transaction']['timestamp'] = timestamp

    assert tx_dict == expected


def test_transaction_deserialization(default_ffill, default_cond):
    from bigchaindb.transaction import Transaction

    tx_id = 'l0l'
    timestamp = '66666666666'

    expected = Transaction(Transaction.CREATE, [default_ffill], [default_cond], None, timestamp, Transaction.VERSION)

    tx = {
        'id': tx_id,
        'version': Transaction.VERSION,
        'transaction': {
            # NOTE: This test assumes that Fulfillments and Conditions can successfully be serialized
            'fulfillments': [default_ffill.to_dict()],
            'conditions': [default_cond.to_dict()],
            'operation': Transaction.CREATE,
            'timestamp': timestamp,
            'data': None,
        }
    }
    tx = Transaction.from_dict(tx)

    assert tx.to_dict() == expected.to_dict()


def test_invalid_tx_initialization():
    from bigchaindb.transaction import Transaction

    wrong_data_type = {'payload': 'a totally wrong datatype'}
    with raises(TypeError):
        Transaction(Transaction.CREATE, wrong_data_type)
    with raises(TypeError):
        Transaction(Transaction.CREATE, [], wrong_data_type)
    with raises(TypeError):
        Transaction(Transaction.CREATE, [], [], wrong_data_type)
