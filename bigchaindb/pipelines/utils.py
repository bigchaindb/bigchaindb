import rethinkdb as r
from pipes import Node

from bigchaindb import Bigchain


class ChangeFeed(Node):

    def __init__(self, table, operation, prefeed=None):
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

            if is_insert and self.operation == 'insert':
                self.outqueue.put(change['new_val'])
            elif is_delete and self.operation == 'delete':
                self.outqueue.put(change['old_val'])
            elif is_update and self.operation == 'update':
                self.outqueue.put(change)

