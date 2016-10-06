def test_settings(monkeypatch):
    import bigchaindb
    from bigchaindb.web import server

    s = server.create_server(bigchaindb.config['server'])

    # for whatever reason the value is wrapped in a list
    # needs further investigation
    assert s.cfg.bind[0] == bigchaindb.config['server']['bind']
