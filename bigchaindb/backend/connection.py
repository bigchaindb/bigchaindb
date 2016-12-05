from bigchaindb.common.exceptions import ConfigurationError
from importlib import import_module


BACKENDS = {
    'rethinkdb': 'bigchaindb.backend.rethinkdb.connection.RethinkDBConnection'
}


def connect(backend, host, port, dbname):
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
