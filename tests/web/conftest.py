import pytest


@pytest.fixture
def app(request):
    from bigchaindb import config
    from bigchaindb.web import server
    from bigchaindb.tendermint.lib import BigchainDB

    if config['database']['backend'] == 'localmongodb':
        app = server.create_app(debug=True, bigchaindb_factory=BigchainDB)
    else:
        app = server.create_app(debug=True)

    return app
