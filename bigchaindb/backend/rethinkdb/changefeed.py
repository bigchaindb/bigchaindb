import time
import logging
import rethinkdb as r

from bigchaindb import backend
from bigchaindb.backend.exceptions import BackendError
from bigchaindb.backend.changefeed import ChangeFeed
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.rethinkdb.connection import RethinkDBConnection


logger = logging.getLogger(__name__)
register_changefeed = module_dispatch_registrar(backend.changefeed)


class RethinkDBChangeFeed(ChangeFeed):
    """This class wraps a RethinkDB changefeed as a multipipes Node."""

    def run_forever(self):
        for element in self.prefeed:
            self.outqueue.put(element)

        for change in run_changefeed(self.connection, self.table):
            is_insert = change['old_val'] is None
            is_delete = change['new_val'] is None
            is_update = not is_insert and not is_delete

            if is_insert and (self.operation & ChangeFeed.INSERT):
                self.outqueue.put(change['new_val'])
            elif is_delete and (self.operation & ChangeFeed.DELETE):
                self.outqueue.put(change['old_val'])
            elif is_update and (self.operation & ChangeFeed.UPDATE):
                self.outqueue.put(change['new_val'])


def run_changefeed(connection, table):
    """Encapsulate operational logic of tailing changefeed from RethinkDB
    """
    while True:
        try:
            for change in connection.run(r.table(table).changes()):
                yield change
            break
        except (BackendError, r.ReqlDriverError) as exc:
            logger.exception('Error connecting to the database, retrying')
            time.sleep(1)


@register_changefeed(RethinkDBConnection)
def get_changefeed(connection, table, operation, *, prefeed=None):
    """Return a RethinkDB changefeed.

    Returns:
        An instance of
        :class:`~bigchaindb.backend.rethinkdb.RethinkDBChangeFeed`.
    """

    return RethinkDBChangeFeed(table, operation, prefeed=prefeed,
                               connection=connection)
