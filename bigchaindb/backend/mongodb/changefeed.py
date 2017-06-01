import logging
import time

import pymongo

from bigchaindb import backend
from bigchaindb.backend.changefeed import ChangeFeed
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.mongodb.connection import MongoDBConnection
from bigchaindb.backend.exceptions import BackendError


logger = logging.getLogger(__name__)
register_changefeed = module_dispatch_registrar(backend.changefeed)


class MongoDBChangeFeed(ChangeFeed):
    """This class implements a MongoDB changefeed as a multipipes Node.

    We emulate the behaviour of the RethinkDB changefeed by using a tailable
    cursor that listens for events on the oplog.
    """
    def run_forever(self):
        for element in self.prefeed:
            self.outqueue.put(element)

        table = self.table
        dbname = self.connection.dbname

        # last timestamp in the oplog. We only care for operations happening
        # in the future.
        last_ts = self.connection.run(
            self.connection.query().local.oplog.rs.find()
            .sort('$natural', pymongo.DESCENDING).limit(1)
            .next()['ts'])

        for record in run_changefeed(self.connection, table, last_ts):

            is_insert = record['op'] == 'i'
            is_delete = record['op'] == 'd'
            is_update = record['op'] == 'u'

            # mongodb documents uses the `_id` for the primary key.
            # We are not using this field at this point and we need to
            # remove it to prevent problems with schema validation.
            # See https://github.com/bigchaindb/bigchaindb/issues/992
            if is_insert and (self.operation & ChangeFeed.INSERT):
                record['o'].pop('_id', None)
                self.outqueue.put(record['o'])
            elif is_delete and (self.operation & ChangeFeed.DELETE):
                # on delete it only returns the id of the document
                self.outqueue.put(record['o'])
            elif is_update and (self.operation & ChangeFeed.UPDATE):
                # the oplog entry for updates only returns the update
                # operations to apply to the document and not the
                # document itself. So here we first read the document
                # and then return it.
                doc = self.connection.conn[dbname][table].find_one(
                    {'_id': record['o2']['_id']},
                    {'_id': False}
                )
                self.outqueue.put(doc)

            logger.debug('Record in changefeed: %s:%s', table, record['op'])


@register_changefeed(MongoDBConnection)
def get_changefeed(connection, table, operation, *, prefeed=None):
    """Return a MongoDB changefeed.

    Returns:
        An instance of
        :class:`~bigchaindb.backend.mongodb.MongoDBChangeFeed`.
    """

    return MongoDBChangeFeed(table, operation, prefeed=prefeed,
                             connection=connection)


_FEED_STOP = False
"""If it's True then the changefeed will return when there are no more items.
"""


def run_changefeed(conn, table, last_ts):
    """Encapsulate operational logic of tailing changefeed from MongoDB
    """
    while True:
        try:
            # XXX: hack to force reconnection, in case the connection
            # is lost while waiting on the cursor. See #1154.
            conn._conn = None
            namespace = conn.dbname + '.' + table
            query = conn.query().local.oplog.rs.find(
                {'ns': namespace, 'ts': {'$gt': last_ts}},
                {'o._id': False},
                cursor_type=pymongo.CursorType.TAILABLE_AWAIT
            )
            cursor = conn.run(query)
            logging.debug('Tailing oplog at %s/%s', namespace, last_ts)
            while cursor.alive:
                try:
                    record = cursor.next()
                    yield record
                    last_ts = record['ts']
                except StopIteration:
                    if _FEED_STOP:
                        return
        except (BackendError, pymongo.errors.ConnectionFailure):
            logger.exception('Lost connection while tailing oplog, retrying')
            time.sleep(1)
