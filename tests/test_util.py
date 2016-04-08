from bigchaindb import util


def test_transform_create(b, user_sk, user_vk):
    tx = util.create_tx(user_vk, user_vk, None, 'CREATE')
    tx = util.transform_create(tx)
    tx = util.sign_tx(tx, b.me_private)

    assert tx['transaction']['fulfillments'][0]['current_owners'][0] == b.me
    assert tx['transaction']['conditions'][0]['new_owners'][0] == user_vk
    assert util.verify_signature(tx)

