"""
Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""

import os
import copy

import pytest


DB_NAME = 'bigchain_test_{}'.format(os.getpid())

CONFIG = {
    'database': {
        'name': DB_NAME
    },
    'keypair': {
        'private': '31Lb1ZGKTyHnmVK3LUMrAUrPNfd4sE2YyBt3UA4A25aA',
        'public': '4XYfCbabAWVUCbjTmRTFEu2sc3dFEdkse4r6X498B1s8'
    }
}

# Test user. inputs will be created for this user. Cryptography Keys
USER_SIGNING_KEY = '8eJ8q9ZQpReWyQT5aFCiwtZ5wDZC4eDnCen88p3tQ6ie'
USER_VERIFYING_KEY = 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE'

USER2_SIGNING_KEY = 'F86PQPiqMTwM2Qi2Sda3U4Vdh3AgadMdX3KNVsu5wNJr'
USER2_VERIFYING_KEY = 'GDxwMFbwdATkQELZbMfW8bd9hbNYMZLyVXA3nur2aNbE'


CC_FULFILLMENT_URI = 'cf:0:'
CC_CONDITION_URI = 'cc:0:3:47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU:0'

PAYLOAD = {
    'msg': 'Hello BigchainDB!'
}
PAYLOAD_ID = '872fa6e6f46246cd44afdb2ee9cfae0e72885fb0910e2bcf9a5a2a4eadb417b8'


# We need this function to avoid loading an existing
# conf file located in the home of the user running
# the tests. If it's too aggressive we can change it
# later.
@pytest.fixture(scope='function', autouse=True)
def ignore_local_config_file(monkeypatch):
    def mock_file_config(filename=None):
        # TODO: FileNotFoundError is not defined anywhere. Import it
        raise FileNotFoundError()

    monkeypatch.setattr('bigchaindb.config_utils.file_config', mock_file_config)


@pytest.fixture(scope='function', autouse=True)
def restore_config(request, node_config):
    from bigchaindb import config_utils
    config_utils.set_config(node_config)


@pytest.fixture(scope='module')
def node_config():
    return copy.deepcopy(CONFIG)


@pytest.fixture
def user_sk():
    return USER_SIGNING_KEY


@pytest.fixture
def user_vk():
    return USER_VERIFYING_KEY


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
def b(request, node_config):
    restore_config(request, node_config)
    from bigchaindb import Bigchain
    return Bigchain()


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
    from bigchaindb.transaction import Fulfillment
    return Fulfillment.gen_default([user_vk])


@pytest.fixture
def default_single_cond(default_single_ffill):
    return default_single_ffill.gen_condition()


@pytest.fixture
def default_threshold_ffill(user_vks):
    from bigchaindb.transaction import Fulfillment
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
    from bigchaindb.transaction import Data
    return Data(payload, payload_id)


@pytest.fixture
def tx(default_single_ffill, default_single_cond):
    from bigchaindb.transaction import Transaction
    return Transaction(Transaction.CREATE, [default_single_ffill], [default_single_cond])
