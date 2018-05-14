from functools import singledispatch

from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection


@singledispatch
def flush_db(connection, dbname):
    raise NotImplementedError


@flush_db.register(LocalMongoDBConnection)
def flush_localmongo_db(connection, dbname):
    connection.conn[dbname].bigchain.delete_many({})
    connection.conn[dbname].blocks.delete_many({})
    connection.conn[dbname].transactions.delete_many({})
    connection.conn[dbname].assets.delete_many({})
    connection.conn[dbname].metadata.delete_many({})
    connection.conn[dbname].utxos.delete_many({})
    connection.conn[dbname].validators.delete_many({})
