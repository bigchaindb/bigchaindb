def test_get_connection_returns_the_correct_instance():
    from bigchaindb.backend import connect
    from bigchaindb.backend.connection import Connection
    from bigchaindb.backend.rethinkdb.connection import RethinkDBConnection

    config = {
        'backend': 'rethinkdb',
        'host': 'localhost',
        'port': 28015,
        'dbname': 'test'
    }

    conn = connect(**config)
    assert isinstance(conn, Connection)
    assert isinstance(conn, RethinkDBConnection)
