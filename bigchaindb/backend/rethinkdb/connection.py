import time
import logging

import rethinkdb as r

from bigchaindb.backend.connection import Connection

logger = logging.getLogger(__name__)


class RethinkDBConnection(Connection):
    """
    This class is a proxy to run queries against the database, it is:

        - lazy, since it creates a connection only when needed
        - resilient, because before raising exceptions it tries
          more times to run the query or open a connection.
    """

    def __init__(self, host, port, dbname, max_tries=3, **kwargs):
        """Create a new :class:`~.RethinkDBConnection` instance.

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
        self.conn = None

    def run(self, query):
        """Run a RethinkDB query.

        Args:
            query: the RethinkDB query.

        Raises:
            :exc:`rethinkdb.ReqlDriverError`: After
                :attr:`~.RethinkDBConnection.max_tries`.
        """

        if self.conn is None:
            self._connect()

        for i in range(self.max_tries):
            try:
                return query.run(self.conn)
            except r.ReqlDriverError:
                if i + 1 == self.max_tries:
                    raise
                self._connect()

    def _connect(self):
        """Set a connection to RethinkDB.

        The connection is available via :attr:`~.RethinkDBConnection.conn`.

        Raises:
            :exc:`rethinkdb.ReqlDriverError`: After
                :attr:`~.RethinkDBConnection.max_tries`.
        """

        for i in range(1, self.max_tries + 1):
            logging.debug('Connecting to database %s:%s/%s. (Attempt %s/%s)',
                          self.host, self.port, self.dbname, i, self.max_tries)
            try:
                self.conn = r.connect(host=self.host, port=self.port, db=self.dbname)
            except r.ReqlDriverError:
                if i == self.max_tries:
                    raise
                wait_time = 2**i
                logging.debug('Error connecting to database, waiting %ss', wait_time)
                time.sleep(wait_time)
            else:
                break
