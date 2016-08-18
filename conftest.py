"""
Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""
import pytest


# Test user. inputs will be created for this user. Cryptography Keys
USER_PRIVATE_KEY = '8eJ8q9ZQpReWyQT5aFCiwtZ5wDZC4eDnCen88p3tQ6ie'
USER_PUBLIC_KEY = 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE'

USER2_PRIVATE_KEY = 'F86PQPiqMTwM2Qi2Sda3U4Vdh3AgadMdX3KNVsu5wNJr'
USER2_PUBLIC_KEY = 'GDxwMFbwdATkQELZbMfW8bd9hbNYMZLyVXA3nur2aNbE'

USER3_PRIVATE_KEY = '4rNQFzWQbVwuTiDVxwuFMvLG5zd8AhrQKCtVovBvcYsB'
USER3_PUBLIC_KEY = 'Gbrg7JtxdjedQRmr81ZZbh1BozS7fBW88ZyxNDy7WLNC'


CC_FULFILLMENT_URI = 'cf:0:'
CC_CONDITION_URI = 'cc:0:3:47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU:0'

PAYLOAD = {
    'msg': 'Hello BigchainDB!'
}
PAYLOAD_ID = '872fa6e6f46246cd44afdb2ee9cfae0e72885fb0910e2bcf9a5a2a4eadb417b8'


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
def user_pub_keys():
    return [USER_PUBLIC_KEY, USER2_PUBLIC_KEY]


@pytest.fixture
def user_priv_keys():
    return [USER_PRIVATE_KEY, USER2_PRIVATE_KEY]


@pytest.fixture
def ffill_uri():
    return CC_FULFILLMENT_URI


@pytest.fixture
def cond_uri():
    return CC_CONDITION_URI


@pytest.fixture
def cc_ffill(ffill_uri, user_pub):
    from cryptoconditions import Fulfillment
    return Fulfillment.from_uri(ffill_uri)


@pytest.fixture
def default_single_ffill(user_pub):
    from bigchaindb_common.transaction import Fulfillment
    return Fulfillment.gen_default([user_pub])


@pytest.fixture
def default_single_cond(default_single_ffill):
    return default_single_ffill.gen_condition()


@pytest.fixture
def default_threshold_ffill(user_pub_keys):
    from bigchaindb_common.transaction import Fulfillment
    return Fulfillment.gen_default(user_pub_keys)


@pytest.fixture
def default_threshold_cond(default_threshold_ffill):
    return default_threshold_ffill.gen_condition()


@pytest.fixture
def payload():
    return PAYLOAD


@pytest.fixture
def payload_id():
    return PAYLOAD_ID


@pytest.fixture
def data(payload, payload_id):
    from bigchaindb_common.transaction import Data
    return Data(payload, payload_id)


@pytest.fixture
def tx(default_single_ffill, default_single_cond):
    from bigchaindb_common.transaction import Transaction
    return Transaction(Transaction.CREATE, [default_single_ffill], [default_single_cond])
