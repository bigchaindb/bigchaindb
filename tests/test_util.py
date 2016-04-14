import pytest


def test_transform_create(b, user_private_key, user_public_key):
    from bigchaindb import util

    tx = util.create_tx(user_public_key, user_public_key, None, 'CREATE')
    tx = util.transform_create(tx)
    tx = util.sign_tx(tx, b.me_private)

    assert tx['transaction']['current_owner'] == b.me
    assert tx['transaction']['new_owner'] == user_public_key
    assert util.verify_signature(tx)

@pytest.mark.skipif(reason='asdf')
def test_pool():
    from bigchaindb import util

    pool = util.pool(lambda: 'hello', limit=4)

    assert pool().__enter__() == 'hello'
    assert pool().__enter__() == 'hello'
    assert pool().__enter__() == 'hello'

