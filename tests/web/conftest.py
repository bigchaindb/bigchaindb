import pytest
from ..db import conftest


@pytest.fixture(autouse=True)
def restore_config(request, node_config):
    from bigchaindb import config_utils
    config_utils.dict_config(node_config)


@pytest.fixture(scope='module', autouse=True)
def setup_database(request, node_config):
    conftest.setup_database(request, node_config)


@pytest.fixture(scope='function', autouse=True)
def cleanup_tables(request, node_config):
    conftest.cleanup_tables(request, node_config)


@pytest.fixture
def app(request, node_config):
    # XXX: For whatever reason this fixture runs before `restore_config`,
    #      so we need to manually call it.
    restore_config(request, node_config)

    from bigchaindb.web import server
    app = server.create_app({'debug': True})
    return app


@pytest.fixture
def inputs(user_public_key):
    conftest.inputs(user_public_key)

