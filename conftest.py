"""
Fixtures and setup / teardown functions

Tasks:
1. setup test database before starting the tests
2. delete test database after running the tests
"""

import pytest

import bigchaindb
import bigchaindb.config_utils


config = {
    'database': {
        'name': 'bigchain_test'
    },
    'keypair': {
        'private': '3i2FDXp87N9ExXSvWxqBAw9EgzoxxGTQNKbtxmWBpTyL',
        'public': '29Tw3ozmSRtN8XNofvsu5RdoQRk9gAonfpkFvRZDmhTPo'
    }
}

# Test user. inputs will be created for this user. Cryptography Keys
USER_PRIVATE_KEY = 'GmRZxQdQv7tooMijXytQkexKuFN6mJocciJarAmMwTX2'
USER_PUBLIC_KEY = 'r3cEu8GNoz8rYpNJ61k7GqfR8VEvdUbtyHce8u1kaYwh'


@pytest.fixture(scope='function', autouse=True)
def restore_config(request):
    bigchaindb.config_utils.dict_config(config)


# FIXME: make this fixtures work :)
# @pytest.fixture
# def config():
#     return config
#
#
# @pytest.fixture
# def user_private_key():
#     return USER_PRIVATE_KEY
#
#
# @pytest.fixture
# def user_public_key():
#     return USER_PUBLIC_KEY
#
