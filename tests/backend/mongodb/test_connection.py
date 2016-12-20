
def test_get_connection_returns_the_correct_instance():
    from bigchaindb.backend import connect
    from bigchaindb.backend.connection import Connection
    from bigchaindb.backend.mongodb.connection import MongoDBConnection

    config = {
        'backend': 'mongodb',
        'host': 'localhost',
        'port': 27017,
        'name': 'test'
    }

    conn = connect(**config)
    assert isinstance(conn, Connection)
    assert isinstance(conn, MongoDBConnection)
