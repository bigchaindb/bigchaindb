import logging
import time

import pymongo
from pymongo.errors import ConnectionFailure, OperationFailure

from bigchaindb import backend
from bigchaindb.backend.changefeed import ChangeFeed
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.mongodb.connection import MongoDBConnection


logger = logging.getLogger(__name__)
register_changefeed = module_dispatch_registrar(backend.changefeed)


class MongoDBChangeFeed(ChangeFeed):
    """This class implements a MongoDB changefeed.

    We emulate the behaviour of the RethinkDB changefeed by using a tailable
    cursor that listens for events on the oplog.
    """

    def run_forever(self):
        for element in self.prefeed:
            self.outqueue.put(element)

        while True:
            try:
                self.run_changefeed()
                break
            except (ConnectionFailure, OperationFailure) as exc:
                logger.exception(exc)
                time.sleep(1)

    def run_changefeed(self):
        # this is kinda a hack to make sure that the connection object is
        # setup
        self.connection._connect()
        # namespace to allow us to only listen to changes in a single
        # collection
        namespace = '{}.{}'.format(self.connection.dbname, self.table)
        # last timestamp in the oplog. We only care for operations happening
        # in the future.
        last_ts = self.connection.conn.local.oplog.rs.find()\
                      .sort('$natural', pymongo.DESCENDING).limit(1)\
                      .next()['ts']
        # tailable cursor. A tailable cursor will remain open even after the
        # last result was returned. ``TAILABLE_AWAIT`` will block for some
        # timeout after the last result was returned. If no result is received
        # in the meantime it will raise a StopIteration excetiption.
        cursor = self.connection.conn.local.oplog.rs.find(
            {'ns': namespace, 'ts': {'$gt': last_ts}},
            cursor_type=pymongo.CursorType.TAILABLE_AWAIT
        )

        while cursor.alive:
            try:
                record = cursor.next()
            except StopIteration:
                continue
            else:
                is_insert = record['op'] == 'i'
                is_delete = record['op'] == 'd'
                is_update = record['op'] == 'u'

                if is_insert and (self.operation & ChangeFeed.INSERT):
                    self.outqueue.put(record['o'])
                elif is_delete and (self.operation & ChangeFeed.DELETE):
                    # on delete it only returns the id of the document
                    self.outqueue.put(record['o'])
                elif is_update and (self.operation & ChangeFeed.UPDATE):
                    # not sure what to do here. Lets return the entire
                    # operation
                    self.outqueue.put(record)


@register_changefeed(MongoDBConnection)
def get_changefeed(connection, table, operation, *, prefeed=None):
    """Return a MongoDB changefeed.

    Returns:
        An instance of
        :class:`~bigchaindb.backend.mongodb.MongoDBChangeFeed`.
    """

    return MongoDBChangeFeed(table, operation, prefeed=prefeed,
                             connection=connection)
