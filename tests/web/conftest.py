import pytest


@pytest.fixture
def app(request):
    from bigchaindb.web import server
    from bigchaindb.lib import BigchainDB

    if request.config.getoption('--database-backend') == 'localmongodb':
        app = server.create_app(debug=True, bigchaindb_factory=BigchainDB)
    else:
        app = server.create_app(debug=True)

    return app
