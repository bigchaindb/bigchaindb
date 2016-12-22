import time
import logging

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from bigchaindb.backend.connection import Connection

logger = logging.getLogger(__name__)


class MongoDBConnection(Connection):

    def __init__(self, host, port, dbname, max_tries=3):
        """Create a new :class:`~.MongoDBConnection` instance.

        See :meth:`.Connection.__init__` for
        :attr:`host`, :attr:`port`, and :attr:`dbname`.

        Args:
            max_tries (int, optional): how many tries before giving up.
                Defaults to 3.
        """

        self.host = host
        self.port = port
        self.dbname = dbname
        self.max_tries = max_tries
        self.connection = None

    @property
    def conn(self):
        if self.connection is None:
            self._connect()
        return self.connection

    @property
    def db(self):
        if self.conn is None:
            self._connect()

        else:
            return self.conn[self.dbname]

    def _connect(self):
        for i in range(self.max_tries):
            try:
                self.connection = MongoClient(self.host, self.port)
            except ConnectionFailure as exc:
                if i + 1 == self.max_tries:
                    raise
                else:
                    time.sleep(2**i)
