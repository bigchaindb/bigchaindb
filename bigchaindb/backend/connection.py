import logging
from importlib import import_module
from copy import copy

import bigchaindb
from bigchaindb.common.exceptions import ConfigurationError


BACKENDS = {
    'mongodb': 'bigchaindb.backend.mongodb.connection.MongoDBConnection',
    'rethinkdb': 'bigchaindb.backend.rethinkdb.connection.RethinkDBConnection'
}

logger = logging.getLogger(__name__)


def connect(**kwargs):
    """Create a new connection to the database backend.

    Uses the current node's configuration (``config.database``) to start the
    connection, unless overridden via keyword arguments.

    Args:
        **kwargs: arbitrary keyword arguments that will override the values
            provided by the node configuration's ``database`` settings.
            For example, giving ``port`` as a keyword argument will override
            the ``config.database.port`` setting.

    Returns:
        An instance of :class:`~bigchaindb.backend.connection.Connection`
        based on the given or defaulted) :attr:`backend`.

    Raises:
        :exc:`~ConfigurationError`: If the given (or defaulted) :attr:`backend`
            is not supported or could not be loaded.
    """

    backend_config = copy(bigchaindb.config['database'])
    backend_config.update(kwargs)

    # We don't want to pass the `backend` property into Connection
    backend = backend_config.pop('backend')
    try:
        module_name, _, class_name = BACKENDS[backend].rpartition('.')
        Class = getattr(import_module(module_name), class_name)
    except KeyError:
        raise ConfigurationError('Backend `{}` is not supported. '
                                 'BigchainDB currently supports {}'.format(backend, BACKENDS.keys()))
    except (ImportError, AttributeError) as exc:
        raise ConfigurationError('Error loading backend `{}`'.format(backend)) from exc

    logger.debug('Connection: {}'.format(Class))
    return Class(**backend_config)


class Connection:
    """Connection class interface.

    All backend implementations should provide a connection class that
    from and implements this class.
    """

    def __init__(self, host, port, dbname, **kwargs):
        """Create a new :class:`~.Connection` instance.

        Args:
            host (str): the host to connect to.
            port (int): the port to connect to.
            dbname (str): the name of the database to use.
            **kwargs: arbitrary keyword arguments provided by the node
                configuration's ``database`` settings or :func:`connect`
        """

    def run(self, query):
        """Run a query.

        Args:
            query: the query to run
        """

        raise NotImplementedError()
