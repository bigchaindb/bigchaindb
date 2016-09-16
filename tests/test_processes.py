def test_start(monkeypatch):
    from unittest.mock import Mock
    from bigchaindb.processes import start

    election = Mock()
    block = Mock()
    vote = Mock()
    create_server = Mock()
    monkeypatch.setattr('bigchaindb.pipelines.election.start', election)
    monkeypatch.setattr('bigchaindb.pipelines.block.start', block)
    monkeypatch.setattr('bigchaindb.pipelines.vote.start', vote)
    monkeypatch.setattr('bigchaindb.web.server.create_server', create_server)

    start()
    assert election.called is True
    assert block.called is True
    assert vote.called is True
    assert create_server.called is True
