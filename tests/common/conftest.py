import pytest


USER_PRIVATE_KEY = '8eJ8q9ZQpReWyQT5aFCiwtZ5wDZC4eDnCen88p3tQ6ie'
USER_PUBLIC_KEY = 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE'

USER2_PRIVATE_KEY = 'F86PQPiqMTwM2Qi2Sda3U4Vdh3AgadMdX3KNVsu5wNJr'
USER2_PUBLIC_KEY = 'GDxwMFbwdATkQELZbMfW8bd9hbNYMZLyVXA3nur2aNbE'

USER3_PRIVATE_KEY = '4rNQFzWQbVwuTiDVxwuFMvLG5zd8AhrQKCtVovBvcYsB'
USER3_PUBLIC_KEY = 'Gbrg7JtxdjedQRmr81ZZbh1BozS7fBW88ZyxNDy7WLNC'


CC_FULFILLMENT_URI = 'cf:0:'
CC_CONDITION_URI = 'cc:0:3:47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU:0'

DATA = {
    'msg': 'Hello BigchainDB!'
}
DATA_ID = '872fa6e6f46246cd44afdb2ee9cfae0e72885fb0910e2bcf9a5a2a4eadb417b8'


@pytest.fixture
def user_priv():
    return USER_PRIVATE_KEY


@pytest.fixture
def user_pub():
    return USER_PUBLIC_KEY


@pytest.fixture
def user2_priv():
    return USER2_PRIVATE_KEY


@pytest.fixture
def user2_pub():
    return USER2_PUBLIC_KEY


@pytest.fixture
def user3_priv():
    return USER3_PRIVATE_KEY


@pytest.fixture
def user3_pub():
    return USER3_PUBLIC_KEY


@pytest.fixture
def ffill_uri():
    return CC_FULFILLMENT_URI


@pytest.fixture
def cond_uri():
    return CC_CONDITION_URI


@pytest.fixture
def user_Ed25519(user_pub):
    from cryptoconditions import Ed25519Fulfillment
    return Ed25519Fulfillment(public_key=user_pub)


@pytest.fixture
def user_user2_threshold(user_pub, user2_pub):
    from cryptoconditions import (ThresholdSha256Fulfillment,
                                  Ed25519Fulfillment)
    user_pub_keys = [user_pub, user2_pub]
    threshold = ThresholdSha256Fulfillment(threshold=len(user_pub_keys))
    for user_pub in user_pub_keys:
        threshold.add_subfulfillment(Ed25519Fulfillment(public_key=user_pub))
    return threshold


@pytest.fixture
def user2_Ed25519(user2_pub):
    from cryptoconditions import Ed25519Fulfillment
    return Ed25519Fulfillment(public_key=user2_pub)


@pytest.fixture
def user_ffill(user_Ed25519, user_pub):
    from bigchaindb_common.transaction import Fulfillment
    return Fulfillment(user_Ed25519, [user_pub])


@pytest.fixture
def user2_ffill(user2_Ed25519, user2_pub):
    from bigchaindb_common.transaction import Fulfillment
    return Fulfillment(user2_Ed25519, [user2_pub])


@pytest.fixture
def user_user2_threshold_cond(user_user2_threshold, user_pub, user2_pub):
    from bigchaindb_common.transaction import Condition
    return Condition(user_user2_threshold, [user_pub, user2_pub])


@pytest.fixture
def user_user2_threshold_ffill(user_user2_threshold, user_pub, user2_pub):
    from bigchaindb_common.transaction import Fulfillment
    return Fulfillment(user_user2_threshold, [user_pub, user2_pub])


@pytest.fixture
def user_cond(user_Ed25519, user_pub):
    from bigchaindb_common.transaction import Condition
    return Condition(user_Ed25519, [user_pub])


@pytest.fixture
def user2_cond(user2_Ed25519, user2_pub):
    from bigchaindb_common.transaction import Condition
    return Condition(user2_Ed25519, [user2_pub])


@pytest.fixture
def data():
    return DATA


@pytest.fixture
def data_id():
    return DATA_ID


@pytest.fixture
def metadata(data, data_id):
    from bigchaindb_common.transaction import Metadata
    return Metadata(data, data_id)


@pytest.fixture
def utx(user_ffill, user_cond):
    from bigchaindb_common.transaction import Transaction, Asset
    return Transaction(Transaction.CREATE, Asset(), [user_ffill], [user_cond])


@pytest.fixture
def tx(utx, user_priv):
    return utx.sign([user_priv])


@pytest.fixture
def transfer_utx(user_cond, user2_cond, utx):
    from bigchaindb_common.transaction import (Fulfillment, TransactionLink,
                                               Transaction, Asset)
    user_cond = user_cond.to_dict()
    ffill = Fulfillment(utx.conditions[0].fulfillment,
                        user_cond['owners_after'],
                        TransactionLink(utx.id, 0))
    return Transaction('TRANSFER', Asset(), [ffill], [user2_cond])


@pytest.fixture
def transfer_tx(transfer_utx, user_priv):
    return transfer_utx.sign([user_priv])
