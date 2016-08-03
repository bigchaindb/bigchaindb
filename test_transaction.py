from pytest import raises


def test_fulfillment_serialization(ffill, user_vk):
    from bigchaindb.transaction import (
        Fulfillment,
    )

    ffill = Fulfillment(ffill, [user_vk])
    ffill_dict = ffill.to_dict()
    assert ffill_dict['owners_before'] == [user_vk]
    assert ffill_dict['input'] == None
    assert ffill_dict['fulfillment'] == ffill.fulfillment.serialize_uri()
    assert ffill_dict['fid'] == 0


def test_fulfillment_deserialization(ffill_uri, user_vk):
    from bigchaindb.transaction import (
        Fulfillment,
    )

    ffill_dict = {
        'owners_before': [user_vk],
        'fulfillment': ffill_uri,
        'fid': 0,
        'input': None,
    }

    assert Fulfillment.from_dict(ffill_dict).to_dict() == ffill_dict


def test_invalid_fulfillment_initialization(ffill, user_vk):
    from bigchaindb.transaction import (
        Fulfillment,
    )
    with raises(TypeError):
        Fulfillment(ffill, user_vk)


def test_condition_serialization(user_vk):
    from bigchaindb.transaction import (
        Condition,
    )

    cond = Condition.gen_default(user_vk)
    cond_dict = cond.to_dict()
    assert cond_dict['owners_after'] == [user_vk]
    assert cond_dict['condition']['uri'] == cond.condition.condition_uri
    assert cond_dict['cid'] == 0


def test_condition_deserialization(user_vk):
    from bigchaindb.transaction import (
        Condition,
    )

    cond = Condition.gen_default(user_vk)
    cond_dict = {
        'condition': {
            'uri': cond.condition.condition_uri,
            'details': cond.condition.to_dict()
        },
        'owners_after': [user_vk],
        'cid': 0,
    }

    assert Condition.from_dict(cond_dict).to_dict() == cond_dict


def test_invalid_condition_initialization(ffill, user_vk):
    from bigchaindb.transaction import (
        Condition,
    )
    with raises(TypeError):
        Condition(ffill.condition, user_vk)


def test_gen_default_condition(user_vk):
    from bigchaindb.transaction import (
        Condition,
    )
    from cryptoconditions import Ed25519Fulfillment
    cond = Condition.gen_default(user_vk)
    assert cond.owners_after == [user_vk]
    assert cond.cid == 0
    # TODO: Would be nice if Cryptoconditions would implement a `__eq__` method
    # NOTE: This doesn't make sense yet...
    assert cond.condition.to_dict() == Ed25519Fulfillment(public_key=user_vk).to_dict()


def test_create_default_transaction(user_vk):
    from bigchaindb.transaction import (
        Condition,
        Transaction,
    )
    cond = Condition.gen_default(user_vk)
    tx = Transaction([cond])
    assert tx.conditions == [cond]
    assert tx.fulfillments == []
    assert tx.inputs is None
    assert tx.payload is None


def test_sign_default_transaction(user_vk, user_sk):
    from bigchaindb.transaction import (
        Fulfillment,
        Transaction,
    )

    ffill = Fulfillment.gen_default(user_vk)
    ffill.to_dict()
    cond = ffill.gen_condition()
    tx = Transaction(Transaction.CREATE, [ffill], [cond])
    tx.sign([user_sk])
    tx_dict = tx.to_dict()
    # TODO: We need to make sure to serialize the transaction correctly!!!
    assert len(tx.fulfillments) > 0
    assert tx_dict['transaction']['conditions'][0] == cond.to_dict()
