from bigchaindb import util


def test_transform_create(b, user_sk, user_vk):
    tx = util.create_tx(user_vk, user_vk, None, 'CREATE')
    tx = util.transform_create(tx)
    tx = util.sign_tx(tx, b.me_private)

    assert tx['transaction']['current_owner'] == b.me
    assert tx['transaction']['new_owner'] == user_vk
    assert util.verify_signature(tx)

