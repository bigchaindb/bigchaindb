import copy
import os

# from functools import reduce
# PORT_NUMBER = reduce(lambda x, y: x * y, map(ord, 'BigchainDB')) % 2**16
# basically, the port number is 9984

_database_rethinkdb = {
    'backend': os.environ.get('BIGCHAINDB_DATABASE_BACKEND', 'rethinkdb'),
    'host': os.environ.get('BIGCHAINDB_DATABASE_HOST', 'localhost'),
    'port': int(os.environ.get('BIGCHAINDB_DATABASE_PORT', 28015)),
    'name': os.environ.get('BIGCHAINDB_DATABASE_NAME', 'bigchain'),
}

_database_mongodb = {
    'backend': os.environ.get('BIGCHAINDB_DATABASE_BACKEND', 'mongodb'),
    'host': os.environ.get('BIGCHAINDB_DATABASE_HOST', 'localhost'),
    'port': int(os.environ.get('BIGCHAINDB_DATABASE_PORT', 27017)),
    'name': os.environ.get('BIGCHAINDB_DATABASE_NAME', 'bigchain'),
    'replicaset': os.environ.get('BIGCHAINDB_DATABASE_REPLICASET', 'bigchain-rs'),
}

_database_map = {
    'mongodb': _database_mongodb,
    'rethinkdb': _database_rethinkdb
}

config = {
    'server': {
        # Note: this section supports all the Gunicorn settings:
        #       - http://docs.gunicorn.org/en/stable/settings.html
        'bind': os.environ.get('BIGCHAINDB_SERVER_BIND') or 'localhost:9984',
        'workers': None,  # if none, the value will be cpu_count * 2 + 1
        'threads': None,  # if none, the value will be cpu_count * 2 + 1
    },
    'database': _database_map[
        os.environ.get('BIGCHAINDB_DATABASE_BACKEND', 'rethinkdb')
    ],
    'keypair': {
        'public': None,
        'private': None,
    },
    'keyring': [],
    'backlog_reassign_delay': 120
}

# We need to maintain a backup copy of the original config dict in case
# the user wants to reconfigure the node. Check ``bigchaindb.config_utils``
# for more info.
_config = copy.deepcopy(config)
from bigchaindb.core import Bigchain  # noqa
from bigchaindb.version import __version__  # noqa
