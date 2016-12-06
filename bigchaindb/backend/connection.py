import bigchaindb
from bigchaindb.common.exceptions import ConfigurationError
from importlib import import_module


BACKENDS = {
    'rethinkdb': 'bigchaindb.backend.rethinkdb.connection.RethinkDBConnection'
}


def connect(backend=None, host=None, port=None, name=None):
    '''Create a connection to a database.

    Args:
        backend (str): the name of the backend to use.
        host (str): the host to connect to.
        port (int): the port to connect to.
        name (str): the name of the database to use.

    Returns:
        An instance of :class:`~bigchaindb.backend.connection.Connection`.
    '''

    backend = backend or bigchaindb.config['database']['backend']
    host = host or bigchaindb.config['database']['host']
    port = port or bigchaindb.config['database']['port']
    dbname = name or bigchaindb.config['database']['name']

    try:
        module_name, _, class_name = BACKENDS[backend].rpartition('.')
        Class = getattr(import_module(module_name), class_name)
    except KeyError:
        raise ConfigurationError('Backend `{}` is not supported. '
                                 'BigchainDB currently supports {}'.format(backend, BACKENDS.keys()))
    except (ImportError, AttributeError) as exc:
        raise ConfigurationError('Error loading backend `{}`'.format(backend)) from exc

    return Class(host, port, dbname)


class Connection:
    pass
