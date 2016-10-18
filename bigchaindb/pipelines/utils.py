"""Utility classes and functions to work with the pipelines."""


import time
import rethinkdb as r
import logging
from multipipes import Node

from bigchaindb import Bigchain


logger = logging.getLogger(__name__)


class ChangeFeed(Node):
    """This class wraps a RethinkDB changefeed adding a ``prefeed``.

    It extends :class:`multipipes.Node` to make it pluggable in other
    Pipelines instances, and makes usage of ``self.outqueue`` to output
    the data.

    A changefeed is a real time feed on inserts, updates, and deletes, and
    is volatile. This class is a helper to create changefeeds. Moreover,
    it provides a way to specify a ``prefeed`` of iterable data to output
    before the actual changefeed.
    """

    INSERT = 1
    DELETE = 2
    UPDATE = 4

    def __init__(self, table, operation, prefeed=None, bigchain=None):
        """Create a new RethinkDB ChangeFeed.

        Args:
            table (str): name of the table to listen to for changes.
            operation (int): can be ChangeFeed.INSERT, ChangeFeed.DELETE, or
                ChangeFeed.UPDATE. Combining multiple operation is possible
                with the bitwise ``|`` operator
                (e.g. ``ChangeFeed.INSERT | ChangeFeed.UPDATE``)
            prefeed (iterable): whatever set of data you want to be published
                first.
            bigchain (``Bigchain``): the bigchain instance to use (can be None).
        """

        super().__init__(name='changefeed')
        self.prefeed = prefeed if prefeed else []
        self.table = table
        self.operation = operation
        self.bigchain = bigchain or Bigchain()

    def run_forever(self):
        for element in self.prefeed:
            self.outqueue.put(element)

        while True:
            try:
                self.run_changefeed()
                break
            except (r.ReqlDriverError, r.ReqlOpFailedError) as exc:
                logger.exception(exc)
                time.sleep(1)

    def run_changefeed(self):
        for change in self.bigchain.connection.run(r.table(self.table).changes()):
            is_insert = change['old_val'] is None
            is_delete = change['new_val'] is None
            is_update = not is_insert and not is_delete

            if is_insert and (self.operation & ChangeFeed.INSERT):
                self.outqueue.put(change['new_val'])
            elif is_delete and (self.operation & ChangeFeed.DELETE):
                self.outqueue.put(change['old_val'])
            elif is_update and (self.operation & ChangeFeed.UPDATE):
                self.outqueue.put(change['new_val'])
