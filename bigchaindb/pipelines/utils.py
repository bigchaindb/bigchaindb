"""Utility classes and functions to work with the pipelines."""


import rethinkdb as r
from multipipes import Node

from bigchaindb import Bigchain


class ChangeFeed(Node):
    """This class wraps a RethinkDB changefeed adding a `prefeed`.

    It extends the ``multipipes::Node`` class to make it pluggable in
    other Pipelines instances, and it makes usage of ``self.outqueue``
    to output the data.

    A changefeed is a real time feed on inserts, updates, and deletes, and
    it's volatile. This class is a helper to create changefeeds. Moreover
    it provides a way to specify a `prefeed`, that is a set of data (iterable)
    to output before the actual changefeed.
    """

    INSERT = 1
    DELETE = 2
    UPDATE = 4

    def __init__(self, table, operation, prefeed=None):
        """Create a new RethinkDB ChangeFeed.

        Args:
            table (str): name of the table to listen to for changes.
            operation (int): can be ChangeFeed.INSERT, ChangeFeed.DELETE, or
                ChangeFeed.UPDATE. Combining multiple operation is possible using
                the bitwise ``|`` operator
                (e.g. ``ChangeFeed.INSERT | ChangeFeed.UPDATE``)
            prefeed (iterable): whatever set of data you want to be published
                first.
        """

        super().__init__(name='changefeed')
        self.prefeed = prefeed if prefeed else []
        self.table = table
        self.operation = operation
        self.bigchain = Bigchain()

    def run_forever(self):
        for element in self.prefeed:
            self.outqueue.put(element)

        for change in r.table(self.table).changes().run(self.bigchain.conn):

            is_insert = change['old_val'] is None
            is_delete = change['new_val'] is None
            is_update = not is_insert and not is_delete

            if is_insert and (self.operation & ChangeFeed.INSERT):
                self.outqueue.put(change['new_val'])
            elif is_delete and (self.operation & ChangeFeed.DELETE):
                self.outqueue.put(change['old_val'])
            elif is_update and (self.operation & ChangeFeed.UPDATE):
                self.outqueue.put(change)

