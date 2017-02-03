"""MongoDB backend implementation.

Contains a MongoDB-specific implementation of the
:mod:`~bigchaindb.backend.changefeed`, :mod:`~bigchaindb.backend.query`, and
:mod:`~bigchaindb.backend.schema` interfaces.

You can specify BigchainDB to use MongoDB as its database backend by either
setting ``database.backend`` to ``'rethinkdb'`` in your configuration file, or
setting the ``BIGCHAINDB_DATABASE_BACKEND`` environment variable to
``'rethinkdb'``.

If configured to use MongoDB, BigchainDB will automatically return instances
of :class:`~bigchaindb.backend.rethinkdb.MongoDBConnection` for
:func:`~bigchaindb.backend.connection.connect` and dispatch calls of the
generic backend interfaces to the implementations in this module.
"""

# Register the single dispatched modules on import.
from bigchaindb.backend.mongodb import admin, schema, query, changefeed  # noqa

# MongoDBConnection should always be accessed via
# ``bigchaindb.backend.connect()``.
