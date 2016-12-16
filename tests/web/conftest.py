import pytest


@pytest.fixture
def app(request, restore_config):
    from bigchaindb.web import server
    app = server.create_app(debug=True)
    return app
