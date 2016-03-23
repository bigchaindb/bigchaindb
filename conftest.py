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
        'private': '3wssdnSNsZYLvvQwuag5QNQnSfc5N38KV1ZeAoeHQQVe59N7vReJwXWANf5nncGxW63UzR4qHHv6DJhyLs9arJng',
        'public': '4spEuJCR6UNkS9Qyz6QwseU3ENRaypkcVgGKDeqfg8Ha'
    }
}

# Test user. inputs will be created for this user. Cryptography Keys
USER_PRIVATE_KEY_ED25519 = '3RZ3Kn8JbzyNwqzDwhU4dkZFFcwVkfgjhKiiqybfabxFAaANZqPemEudxTYMKfkbrHADTGCkvR7uQHSjihsXLbcM'
USER_PUBLIC_KEY_ED25519 = '2XJT5M6D3fYhvDbgcHmGMUcrGeZ9MtCWGqQZZVXghjv9'


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

