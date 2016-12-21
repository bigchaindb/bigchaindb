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
    connection.conn[dbname].bigchain.delete_many({})
    connection.conn[dbname].backlog.delete_many({})
    connection.conn[dbname].votes.delete_many({})


@singledispatch
def update_table_config(connection, table, **kwrgas):
    raise NotImplementedError


@update_table_config.register(RethinkDBConnection)
def update_table_config(connection, table, **kwargs):
    return connection.run(r.table(table).config().update(dict(**kwargs)))
