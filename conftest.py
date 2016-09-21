import pytest


USER_PRIVATE_KEY = '8eJ8q9ZQpReWyQT5aFCiwtZ5wDZC4eDnCen88p3tQ6ie'
USER_PUBLIC_KEY = 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE'


# We need this function to avoid loading an existing
# conf file located in the home of the user running
# the tests. If it's too aggressive we can change it
# later.
@pytest.fixture(scope='function', autouse=True)
def ignore_local_config_file(monkeypatch):
    def mock_file_config(filename=None):
        raise FileNotFoundError()

    monkeypatch.setattr('bigchaindb.config_utils.file_config', mock_file_config)

USER2_SIGNING_KEY = 'F86PQPiqMTwM2Qi2Sda3U4Vdh3AgadMdX3KNVsu5wNJr'
USER2_VERIFYING_KEY = 'GDxwMFbwdATkQELZbMfW8bd9hbNYMZLyVXA3nur2aNbE'


CC_FULFILLMENT_URI = 'cf:0:'
CC_CONDITION_URI = 'cc:0:3:47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU:0'

PAYLOAD = {
    'msg': 'Hello BigchainDB!'
}
PAYLOAD_ID = '872fa6e6f46246cd44afdb2ee9cfae0e72885fb0910e2bcf9a5a2a4eadb417b8'


@pytest.fixture
def user_private_key():
    return USER_PRIVATE_KEY


@pytest.fixture
def user_public_key():
    return USER_PUBLIC_KEY


@pytest.fixture
def user2_sk():
    return USER2_SIGNING_KEY


@pytest.fixture
def user2_vk():
    return USER2_VERIFYING_KEY


@pytest.fixture
def user_vks():
    return [USER_VERIFYING_KEY, USER2_VERIFYING_KEY]


@pytest.fixture
def user_sks():
    return [USER_SIGNING_KEY, USER2_SIGNING_KEY]


@pytest.fixture
def ffill_uri():
    return CC_FULFILLMENT_URI


@pytest.fixture
def cond_uri():
    return CC_CONDITION_URI


@pytest.fixture
def cc_ffill(ffill_uri, user_vk):
    from cryptoconditions import Fulfillment
    return Fulfillment.from_uri(ffill_uri)


@pytest.fixture
def default_single_ffill(user_vk):
    from bigchaindb_common.transaction import Fulfillment
    return Fulfillment.gen_default([user_vk])


@pytest.fixture
def default_single_cond(default_single_ffill):
    return default_single_ffill.gen_condition()


@pytest.fixture
def default_threshold_ffill(user_vks):
    from bigchaindb_common.transaction import Fulfillment
    return Fulfillment.gen_default(user_vks)


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
def utx(default_single_ffill, default_single_cond):
    from bigchaindb_common.transaction import Transaction
    return Transaction(Transaction.CREATE, [default_single_ffill], [default_single_cond])


@pytest.fixture
def transfer_utx(utx):
    from bigchaindb_common.transaction import Condition
    from cryptoconditions import Ed25519Fulfillment

    cond = Condition(Ed25519Fulfillment(public_key=user2_pub).condition_uri, [user2_pub])
    return utx.transfer([cond])


@pytest.fixture
def transfer_tx(utx, user2_pub, user_priv):
    from bigchaindb_common.transaction import Condition
    from cryptoconditions import Ed25519Fulfillment

    cond = Condition(Ed25519Fulfillment(public_key=user2_pub).condition_uri, [user2_pub])
    return utx.transfer([cond]).sign([user_priv])
