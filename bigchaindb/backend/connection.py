from importlib import import_module
import logging

import bigchaindb
from bigchaindb.common.exceptions import ConfigurationError


BACKENDS = {
    'mongodb': 'bigchaindb.backend.mongodb.connection.MongoDBConnection',
    'rethinkdb': 'bigchaindb.backend.rethinkdb.connection.RethinkDBConnection'
}

logger = logging.getLogger(__name__)


def connect(backend=None, host=None, port=None, name=None, replicaset=None):
    """Create a new connection to the database backend.

    All arguments default to the current configuration's values if not
    given.

    Args:
        backend (str): the name of the backend to use.
        host (str): the host to connect to.
        port (int): the port to connect to.
        name (str): the name of the database to use.
        replicaset (str): the name of the replica set (only relevant for
                          MongoDB connections).

    Returns:
        An instance of :class:`~bigchaindb.backend.connection.Connection`
        based on the given (or defaulted) :attr:`backend`.

    Raises:
        :exc:`~ConnectionError`: If the connection to the database fails.
        :exc:`~ConfigurationError`: If the given (or defaulted) :attr:`backend`
            is not supported or could not be loaded.
    """

    backend = backend or bigchaindb.config['database']['backend']
    host = host or bigchaindb.config['database']['host']
    port = port or bigchaindb.config['database']['port']
    dbname = name or bigchaindb.config['database']['name']
    # Not sure how to handle this here. This setting is only relevant for
    # mongodb.
    # I added **kwargs for both RethinkDBConnection and MongoDBConnection
    # to handle these these additional args. In case of RethinkDBConnection
    # it just does not do anything with it.
    replicaset = replicaset or bigchaindb.config['database'].get('replicaset')

    try:
        module_name, _, class_name = BACKENDS[backend].rpartition('.')
        Class = getattr(import_module(module_name), class_name)
    except KeyError:
        raise ConfigurationError('Backend `{}` is not supported. '
                                 'BigchainDB currently supports {}'.format(backend, BACKENDS.keys()))
    except (ImportError, AttributeError) as exc:
        raise ConfigurationError('Error loading backend `{}`'.format(backend)) from exc

    logger.debug('Connection: {}'.format(Class))
    return Class(host, port, dbname, replicaset=replicaset)


class Connection:
    """Connection class interface.

    All backend implementations should provide a connection class that
    from and implements this class.
    """

    def __init__(self, host=None, port=None, dbname=None, *args, **kwargs):
        """Create a new :class:`~.Connection` instance.

        Args:
            host (str): the host to connect to.
            port (int): the port to connect to.
            dbname (str): the name of the database to use.
            **kwargs: arbitrary keyword arguments provided by the
                configuration's ``database`` settings
        """

    def run(self, query):
        """Run a query.

        Args:
            query: the query to run
        Raises:
            :exc:`~DuplicateKeyError`: If the query fails because of a
                duplicate key constraint.
            :exc:`~OperationFailure`: If the query fails for any other
                reason.
            :exc:`~ConnectionError`: If the connection to the database
                fails.
        """

        raise NotImplementedError()
