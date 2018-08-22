# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

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
