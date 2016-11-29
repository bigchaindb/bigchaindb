from importlib import import_module

BACKENDS = {
    'rethinkdb': 'bigchaindb.backend.rethinkdb.connection.RethinkDBConnection'
}


def connect(backend, host, port, dbname):
    module_name, _, class_name = BACKENDS[backend].rpartition('.')
    Class = getattr(import_module(module_name), class_name)
    return Class(host, port, dbname)


class Connection:
    pass
