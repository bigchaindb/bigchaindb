import pytest


def test_get_connection_returns_the_correct_instance():
    from bigchaindb.backend import connect
    from bigchaindb.backend.connection import Connection
    from bigchaindb.backend.rethinkdb.connection import RethinkDBConnection

    config = {
        'backend': 'rethinkdb',
        'host': 'localhost',
        'port': 28015,
        'name': 'test'
    }

    conn = connect(**config)
    assert isinstance(conn, Connection)
    assert isinstance(conn, RethinkDBConnection)


def test_get_connection_raises_a_configuration_error(monkeypatch):
    from bigchaindb.common.exceptions import ConfigurationError
    from bigchaindb.backend import connect

    with pytest.raises(ConfigurationError):
        connect('msaccess', 'localhost', '1337', 'mydb')

    with pytest.raises(ConfigurationError):
        # We need to force a misconfiguration here
        monkeypatch.setattr('bigchaindb.backend.connection.BACKENDS',
                            {'catsandra': 'bigchaindb.backend.meowmeow.Catsandra'})

        connect('catsandra', 'localhost', '1337', 'mydb')
