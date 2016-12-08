import pytest
from bigchaindb.pipelines import block, election, vote, stale

# TODO: fix this import madness
from ..db import conftest


@pytest.fixture(scope='module', autouse=True)
def restore_config(request, node_config):
    from bigchaindb import config_utils
    config_utils.set_config(node_config)


@pytest.fixture(scope='module', autouse=True)
def setup_database(request, node_config):
    conftest.setup_database(request, node_config)


@pytest.fixture(scope='function', autouse=True)
def cleanup_tables(request, node_config):
    conftest.cleanup_tables(request, node_config)


@pytest.fixture
def processes(b):
    b.create_genesis_block()
    block_maker = block.start()
    voter = vote.start()
    election_runner = election.start()
    stale_monitor = stale.start()
    yield
    block_maker.terminate()
    voter.terminate()
    election_runner.terminate()
    stale_monitor.terminate()
