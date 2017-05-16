import rethinkdb as r

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

        try:
            return r.connect(host=self.host, port=self.port, db=self.dbname)
        except r.ReqlDriverError as exc:
            raise ConnectionError from exc

    @property
    def local_table_suffix(self):
        """Get local table suffix"""
        if not RethinkDBConnection._LOCAL_TABLE_SUFFIX:
            suffix = self.conn.server()['id'].replace('-', '_')
            RethinkDBConnection._LOCAL_TABLE_SUFFIX = suffix
        return RethinkDBConnection._LOCAL_TABLE_SUFFIX

    _LOCAL_TABLE_SUFFIX = None

    def local_table(self, name):
        """Namespace a table to local db server"""
        return '%s_%s' % (name, self.local_table_suffix)
