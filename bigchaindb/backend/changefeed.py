"""Changefeed interfaces for backends."""

from functools import singledispatch

from multipipes import Node

import bigchaindb


class ChangeFeed(Node):
    """Create a new changefeed.

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

    def __init__(self, table, operation, *, prefeed=None, connection=None):
        """Create a new ChangeFeed.

        Args:
            table (str): name of the table to listen to for changes.
            operation (int): can be ChangeFeed.INSERT, ChangeFeed.DELETE, or
                ChangeFeed.UPDATE. Combining multiple operations is possible
                with the bitwise ``|`` operator
                (e.g. ``ChangeFeed.INSERT | ChangeFeed.UPDATE``)
            prefeed (:class:`~collections.abc.Iterable`, optional): whatever
                set of data you want to be published first.
            connection (:class:`~bigchaindb.backend.connection.Connection`, optional):  # noqa
                A connection to the database. If no connection is provided a
                default connection will be created.
        """

        super().__init__(name='changefeed')
        self.prefeed = prefeed if prefeed else []
        self.table = table
        self.operation = operation
        if connection:
            self.connection = connection
        else:
            self.connection = bigchaindb.backend.connect(
                **bigchaindb.config['database'])

    def run_forever(self):
        """Main loop of the ``multipipes.Node``

        This method is responsible for first feeding the prefeed to the
        outqueue and after that starting the changefeed and recovering from any
        errors that may occur in the backend.
        """
        raise NotImplementedError

    def run_changefeed(self):
        """Backend specific method to run the changefeed.

        The changefeed is usually a backend cursor that is not closed when all
        the results are exausted. Instead it remains open waiting for new
        results.

        This method should also filter each result based on the ``operation``
        and put all matching results on the outqueue of ``multipipes.Node``.
        """
        raise NotImplementedError


@singledispatch
def get_changefeed(connection, table, operation, *, prefeed=None):
    """Return a ChangeFeed.

    Args:
        connection (:class:`~bigchaindb.backend.connection.Connection`):
            A connection to the database.
        table (str): name of the table to listen to for changes.
        operation (int): can be ChangeFeed.INSERT, ChangeFeed.DELETE, or
            ChangeFeed.UPDATE. Combining multiple operation is possible
            with the bitwise ``|`` operator
            (e.g. ``ChangeFeed.INSERT | ChangeFeed.UPDATE``)
        prefeed (iterable): whatever set of data you want to be published
            first.
    """
    raise NotImplementedError
