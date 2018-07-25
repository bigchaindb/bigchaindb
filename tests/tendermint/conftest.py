import pytest


@pytest.fixture
def b():
    from bigchaindb import BigchainDB
    return BigchainDB()


@pytest.fixture
def validator_pub_key():
    return 'B0E42D2589A455EAD339A035D6CE1C8C3E25863F268120AA0162AD7D003A4014'
