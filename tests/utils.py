from functools import singledispatch

import rethinkdb as r

from bigchaindb.backend.mongodb.connection import MongoDBConnection
from bigchaindb.backend.rethinkdb.connection import RethinkDBConnection


@singledispatch
def list_dbs(connection):
    raise NotImplementedError


@list_dbs.register(RethinkDBConnection)
def list_rethink_dbs(connection):
    return connection.run(r.db_list())


@list_dbs.register(MongoDBConnection)
def list_mongo_dbs(connection):
    raise NotImplementedError


@singledispatch
def flush_db(connection, dbname):
    raise NotImplementedError


@flush_db.register(RethinkDBConnection)
def flush_rethink_db(connection, dbname):
    try:
        connection.run(r.db(dbname).table('bigchain').delete())
        connection.run(r.db(dbname).table('backlog').delete())
        connection.run(r.db(dbname).table('votes').delete())
    except r.ReqlOpFailedError:
        pass


@flush_db.register(MongoDBConnection)
def flush_mongo_db(connection, dbname):
    raise NotImplementedError
