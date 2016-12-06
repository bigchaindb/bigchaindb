import time
import logging

import rethinkdb as r

from bigchaindb.backend.connection import Connection

logger = logging.getLogger(__name__)


class RethinkDBConnection(Connection):
    """This class is a proxy to run queries against the database,
    it is:
    - lazy, since it creates a connection only when needed
    - resilient, because before raising exceptions it tries
      more times to run the query or open a connection.
    """

    def __init__(self, host, port, dbname, max_tries=3):
        """Create a new Connection instance.

        Args:
            host (str, optional): the host to connect to.
            port (int, optional): the port to connect to.
            dbname (str, optional): the name of the database to use.
            max_tries (int, optional): how many tries before giving up.
        """

        self.host = host
        self.port = port
        self.dbname = dbname
        self.max_tries = max_tries
        self.conn = None

    def run(self, query):
        """Run a query.

        Args:
            query: the RethinkDB query.
        """

        if self.conn is None:
            self._connect()

        for i in range(self.max_tries):
            try:
                return query.run(self.conn)
            except r.ReqlDriverError as exc:
                if i + 1 == self.max_tries:
                    raise
                else:
                    self._connect()

    def _connect(self):
        for i in range(self.max_tries):
            try:
                self.conn = r.connect(host=self.host, port=self.port, db=self.dbname)
            except r.ReqlDriverError as exc:
                if i + 1 == self.max_tries:
                    raise
                else:
                    time.sleep(2**i)
