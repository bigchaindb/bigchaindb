import time
import logging

from pymongo import MongoClient
from pymongo.errors import ConnectionError

import bigchaindb
from bigchaindb.backend.connection import Connection

logger = logging.getLogger(__name__)

class MongoDBConnection(Connection):

    def __init__(self, host=None, port=None, db=None, max_tries=3):
        """Create a new Connection instance.

        Args:
            host (str, optional): the host to connect to.
            port (int, optional): the port to connect to.
            db (str, optional): the database to use.
            max_tries (int, optional): how many tries before giving up.
        """

        self.host = host or bigchaindb.config['database']['host']
        self.port = port or bigchaindb.config['database']['port']
        self.db = db or bigchaindb.config['database']['name']
        self.max_tries = max_tries
        self.conn = None

    @property
    def db(self):
        if self.conn is None:
            self._connect()

        else:
            return self.conn[self.db]

    def _connect(self):
        for i in range(self.max_tries):
            try:
                self.conn = MongoClient(self.host, self.port)
            except ConnectionError as exc:
                if i + 1 == self.max_tries:
                    raise
                else:
                    time.sleep(2**i)
