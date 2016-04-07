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
        'private': '3i2FDXp87N9ExXSvWxqBAw9EgzoxxGTQNKbtxmWBpTyL',
        'public': '29Tw3ozmSRtN8XNofvsu5RdoQRk9gAonfpkFvRZDmhTPo'
    }
}

# Test user. inputs will be created for this user. Cryptography Keys
USER_PRIVATE_KEY = 'GmRZxQdQv7tooMijXytQkexKuFN6mJocciJarAmMwTX2'
USER_PUBLIC_KEY = 'r3cEu8GNoz8rYpNJ61k7GqfR8VEvdUbtyHce8u1kaYwh'


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
    return copy.deepcopy(CONFIG)


@pytest.fixture
def user_private_key():
    return USER_PRIVATE_KEY


@pytest.fixture
def user_public_key():
    return USER_PUBLIC_KEY


@pytest.fixture
def b(request, node_config):
    restore_config(request, node_config)
    from bigchaindb import Bigchain
    return Bigchain()

