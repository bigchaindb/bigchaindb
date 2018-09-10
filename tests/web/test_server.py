# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


def test_settings():
    import bigchaindb
    from bigchaindb.web import server

    s = server.create_server(bigchaindb.config['server'])

    # for whatever reason the value is wrapped in a list
    # needs further investigation
    assert s.cfg.bind[0] == bigchaindb.config['server']['bind']
