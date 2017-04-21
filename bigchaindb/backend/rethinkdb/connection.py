import rethinkdb as r
import time
import bigchaindb

from bigchaindb.backend.connection import Connection
from bigchaindb.backend.exceptions import ConnectionError, OperationError


class RethinkDBConnection(Connection):
    """
    This class is a proxy to run queries against the database, it is:

        - lazy, since it creates a connection only when needed
        - resilient, because before raising exceptions it tries
          more times to run the query or open a connection.
    """

    def run(self, query):
        """Run a RethinkDB query.

        Args:
            query: the RethinkDB query.

        Raises:
            :exc:`rethinkdb.ReqlDriverError`: After
                :attr:`~.RethinkDBConnection.max_tries`.
        """

        try:
            return query.run(self.conn)
        except r.ReqlDriverError as exc:
            raise OperationError from exc

    def _connect(self):
        """Set a connection to RethinkDB.

        The connection is available via :attr:`~.RethinkDBConnection.conn`.

        Raises:
            :exc:`rethinkdb.ReqlDriverError`: After
                :attr:`~.RethinkDBConnection.max_tries`.
        """
        connected=False
        dbconf = bigchaindb.config['database']
        timeout = dbconf['connection_timeout']
        end_time = time.time()*1000 + timeout
        while not connected:
            try:
                rconn=r.connect(host=self.host, port=self.port, db=self.dbname)
                connected=True
            except r.ReqlDriverError as exc:
                if time.time()*1000 > end_time:
                    raise ConnectionError from exc
                pass
        return rconn
