# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest


def test_get_connection_raises_a_configuration_error(monkeypatch):
    from bigchaindb.common.exceptions import ConfigurationError
    from bigchaindb.backend import connect

    with pytest.raises(ConfigurationError):
        connect('msaccess', 'localhost', '1337', 'mydb')

    with pytest.raises(ConfigurationError):
        # We need to force a misconfiguration here
        monkeypatch.setattr('bigchaindb.backend.connection.BACKENDS',
                            {'catsandra':
                             'bigchaindb.backend.meowmeow.Catsandra'})

        connect('catsandra', 'localhost', '1337', 'mydb')
