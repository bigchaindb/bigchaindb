import importlib

ENGINES = {
    'rethinkdb': 'bigchaindb.db.rethinkdb.factory.RethinkDBFactory',
    'mongodb': 'bigchaindb.db.rethinkdb.factory.MongoDBFactory'
}


class BackendFactory:

    def get_connection(self):
        raise NotImplementedError()

    def get_query(self):
        raise NotImplementedError()

    def get_schema(self):
        raise NotImplementedError()


def get_backend_factory(**kwargs):
    full_path = ENGINES[kwargs.pop('engine')]
    package, _, class_name = full_path.rpartition('.')
    backend_class = getattr(importlib.import_module(package), class_name)
    return backend_class(**kwargs)
