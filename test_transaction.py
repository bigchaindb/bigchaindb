from pytest import raises


def test_fulfillment_serialization(ffill_uri, user_vk):
    from bigchaindb.transaction import (
        Fulfillment,
    )

    ffill = Fulfillment(ffill_uri, [user_vk])
    ffill_dict = ffill.to_dict()
    assert ffill_dict['owners_before'] == [user_vk]
    assert ffill_dict['input'] == None
    assert ffill_dict['fulfillment'] == ffill_uri
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


def test_invalid_fulfillment_initialization(ffill_uri, user_vk):
    from bigchaindb.transaction import (
        Fulfillment,
    )
    with raises(TypeError):
        Fulfillment(ffill_uri, user_vk)


def test_condition_serialization(cond_uri, user_vk):
    from bigchaindb.transaction import (
        Condition,
    )

    cond = Condition(cond_uri, [user_vk])
    cond_dict = cond.to_dict()
    assert cond_dict['owners_after'] == [user_vk]
    assert cond_dict['condition']['uri'] == cond_uri
    assert cond_dict['cid'] == 0


def test_condition_deserialization(cond_uri, user_vk):
    from bigchaindb.transaction import (
        Condition,
    )
    from cryptoconditions import (
        Condition as CCCondition,
    )

    cond_dict = {
        'condition': {
            'uri': cond_uri,
            'details': CCCondition.from_uri(cond_uri).to_dict()
        },
        'owners_after': [user_vk],
        'cid': 0,
    }

    assert Condition.from_dict(cond_dict).to_dict() == cond_dict


def test_invalid_condition_initialization(cond_uri, user_vk):
    from bigchaindb.transaction import (
        Condition,
    )
    with raises(TypeError):
        Condition(cond_uri, user_vk)


def test_gen_default_condition(user_vk):
    from bigchaindb.transaction import (
        Condition,
    )
    from cryptoconditions import Ed25519Fulfillment
    cond = Condition.gen_default_condition(user_vk)
    assert cond.owners_after == [user_vk]
    assert cond.cid == 0
    # TODO: Would be nice if Cryptoconditions would implement a `__eq__` method
    assert cond.condition.to_dict() == Ed25519Fulfillment(public_key=user_vk).condition.to_dict()
