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
    """This class implements a MongoDB changefeed.

    We emulate the behaviour of the RethinkDB changefeed by using a tailable
    cursor that listens for events on the oplog.
    """

    def run_forever(self):
        for element in self.prefeed:
            self.outqueue.put(element)

        while True:
            try:
                # XXX: hack to force reconnection. Why? Because the cursor
                # in `run_changefeed` does not run in the context of a
                # Connection object, so if the connection is lost we need
                # to manually reset the connection to None.
                # See #1154
                self.connection.connection = None
                self.run_changefeed()
                break
            except (BackendError, pymongo.errors.ConnectionFailure):
                logger.exception('Error connecting to the database, retrying')
                time.sleep(1)

    def run_changefeed(self):
        dbname = self.connection.dbname
        table = self.table
        namespace = '{}.{}'.format(dbname, table)
        # last timestamp in the oplog. We only care for operations happening
        # in the future.
        last_ts = self.connection.run(
            self.connection.query().local.oplog.rs.find()
            .sort('$natural', pymongo.DESCENDING).limit(1)
            .next()['ts'])
        # tailable cursor. A tailable cursor will remain open even after the
        # last result was returned. ``TAILABLE_AWAIT`` will block for some
        # timeout after the last result was returned. If no result is received
        # in the meantime it will raise a StopIteration excetiption.
        cursor = self.connection.run(
            self.connection.query().local.oplog.rs.find(
                {'ns': namespace, 'ts': {'$gt': last_ts}},
                cursor_type=pymongo.CursorType.TAILABLE_AWAIT
            ))

        while cursor.alive:
            try:
                record = cursor.next()
            except StopIteration:
                continue

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
                    {'_id': record['o2']},
                    {'_id': False}
                )
                self.outqueue.put(doc)


@register_changefeed(MongoDBConnection)
def get_changefeed(connection, table, operation, *, prefeed=None):
    """Return a MongoDB changefeed.

    Returns:
        An instance of
        :class:`~bigchaindb.backend.mongodb.MongoDBChangeFeed`.
    """

    return MongoDBChangeFeed(table, operation, prefeed=prefeed,
                             connection=connection)
