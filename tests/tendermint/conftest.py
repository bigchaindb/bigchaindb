import pytest


@pytest.fixture
def b():
    from bigchaindb.tendermint import BigchainDB
    return BigchainDB()


@pytest.fixture
def merlin():
    from bigchaindb.common.crypto import generate_key_pair
    return generate_key_pair()


@pytest.fixture
def merlin_privkey(merlin):
    return merlin.private_key


@pytest.fixture
def merlin_pubkey(merlin):
    return merlin.public_key


@pytest.fixture
def validator_pub_key():
    return 'B0E42D2589A455EAD339A035D6CE1C8C3E25863F268120AA0162AD7D003A4014'
