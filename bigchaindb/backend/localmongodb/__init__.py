"""MongoDB backend implementation.

Contains a MongoDB-specific implementation of the
:mod:`~bigchaindb.backend.schema` and :mod:`~bigchaindb.backend.query` interfaces.

You can specify BigchainDB to use MongoDB as its database backend by either
setting ``database.backend`` to ``'localmongodb'`` in your configuration file, or
setting the ``BIGCHAINDB_DATABASE_BACKEND`` environment variable to
``'localmongodb'``.

MongoDB is the default database backend for BigchainDB.

If configured to use MongoDB, BigchainDB will automatically return instances
of :class:`~bigchaindb.backend.localmongodb.LocalMongoDBConnection` for
:func:`~bigchaindb.backend.connection.connect` and dispatch calls of the
generic backend interfaces to the implementations in this module.
"""

# Register the single dispatched modules on import.
from bigchaindb.backend.localmongodb import schema, query # noqa

# MongoDBConnection should always be accessed via
# ``bigchaindb.backend.connect()``.
