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

CONFIG_ECDSA = {
    'database': {
        'name': DB_NAME
    },
    'keypair': {
        'private': '3i2FDXp87N9ExXSvWxqBAw9EgzoxxGTQNKbtxmWBpTyL',
        'public': '29Tw3ozmSRtN8XNofvsu5RdoQRk9gAonfpkFvRZDmhTPo'
    }
}

# Test user. inputs will be created for this user. Cryptography Keys
USER_PRIVATE_KEY_ECDSA = 'GmRZxQdQv7tooMijXytQkexKuFN6mJocciJarAmMwTX2'
USER_PUBLIC_KEY_ECDSA = 'r3cEu8GNoz8rYpNJ61k7GqfR8VEvdUbtyHce8u1kaYwh'

CONFIG_ED25519 = {
    'database': {
        'name': DB_NAME
    },
    'keypair': {
        'private': '31Lb1ZGKTyHnmVK3LUMrAUrPNfd4sE2YyBt3UA4A25aA',
        'public': '4XYfCbabAWVUCbjTmRTFEu2sc3dFEdkse4r6X498B1s8'
    }
}

# Test user. inputs will be created for this user. Cryptography Keys
USER_PRIVATE_KEY_ED25519 = '8eJ8q9ZQpReWyQT5aFCiwtZ5wDZC4eDnCen88p3tQ6ie'
USER_PUBLIC_KEY_ED25519 = 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE'


# We need this function to avoid loading an existing
# conf file located in the home of the user running
# the tests. If it's too aggressive we can change it
# later.
@pytest.fixture(scope='function', autouse=True)
def ignore_local_config_file(monkeypatch):
    def mock_file_config(filename=None):
        raise FileNotFoundError()

    monkeypatch.setattr('bigchaindb.config_utils.file_config', mock_file_config)


@pytest.fixture
def restore_config(request, node_config):
    from bigchaindb import config_utils
    config_utils.dict_config(node_config)


@pytest.fixture(scope='module')
def node_config():
    return copy.deepcopy(CONFIG_ED25519)


@pytest.fixture
def user_private_key():
    return USER_PRIVATE_KEY_ED25519


@pytest.fixture
def user_public_key():
    return USER_PUBLIC_KEY_ED25519


@pytest.fixture
def b(request, node_config):
    restore_config(request, node_config)
    from bigchaindb import Bigchain
    return Bigchain()

