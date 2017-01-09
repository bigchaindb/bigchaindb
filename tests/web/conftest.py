import pytest


@pytest.fixture
def app(request):
    from bigchaindb.web import server
    app = server.create_app(debug=True)
    return app
