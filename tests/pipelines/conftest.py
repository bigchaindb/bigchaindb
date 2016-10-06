import pytest
from ..db import conftest


@pytest.fixture(autouse=True)
def restore_config(request, node_config):
    from bigchaindb import config_utils
    config_utils.set_config(node_config)


@pytest.fixture(scope='module', autouse=True)
def setup_database(request, node_config):
    conftest.setup_database(request, node_config)


@pytest.fixture(scope='function', autouse=True)
def cleanup_tables(request, node_config):
    conftest.cleanup_tables(request, node_config)
