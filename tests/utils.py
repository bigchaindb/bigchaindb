# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

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
