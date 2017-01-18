import time
import logging

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

import bigchaindb
from bigchaindb.backend.connection import Connection
from bigchaindb.backend import mongodb

logger = logging.getLogger(__name__)


class MongoDBConnection(Connection):

    def __init__(self, host=None, port=None, dbname=None, max_tries=3,
                 replicaset=None):
        """Create a new Connection instance.

        Args:
            host (str, optional): the host to connect to.
            port (int, optional): the port to connect to.
            dbname (str, optional): the database to use.
            max_tries (int, optional): how many tries before giving up.
            replicaset (str, optional): the name of the replica set to
                                        connect to.
        """

        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.replicaset = replicaset or bigchaindb.config['database']['replicaset']
        self.dbname = dbname or bigchaindb.config['database']['name']
        self.max_tries = max_tries
        self.connection = None

    @property
    def conn(self):
        if self.connection is None:
            self._connect()
        return self.connection

    @property
    def db(self):
        return self.conn[self.dbname]

    def _connect(self):
        for i in range(self.max_tries):
            try:
                # we should only return a connection if the replica set is
                # initialized. initialize_replica_set will check if the
                # replica set is initialized else it will initialize it.
                mongodb.schema.initialize_replica_set()
                self.connection = MongoClient(self.host, self.port,
                                              replicaset=self.replicaset)
            except ConnectionFailure as exc:
                if i + 1 == self.max_tries:
                    raise
                else:
                    time.sleep(2**i)
