import pytest


@pytest.fixture
def b():
    from bigchaindb.tendermint import BigchainDB
    return BigchainDB()
