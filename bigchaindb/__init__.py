import copy
import logging

from bigchaindb.log.configs import SUBSCRIBER_LOGGING_CONFIG as log_config

# from functools import reduce
# PORT_NUMBER = reduce(lambda x, y: x * y, map(ord, 'BigchainDB')) % 2**16
# basically, the port number is 9984


_base_database_rethinkdb = {
    'host': 'localhost',
    'port': 28015,
    'name': 'bigchain',
}

# The following variable is used by `bigchaindb configure` to
# prompt the user for database values. We cannot rely on
# _base_database_rethinkdb.keys() or _base_database_mongodb.keys()
# because dicts are unordered. I tried to configure

_database_keys_map = {
    'localmongodb': ('host', 'port', 'name'),
    'mongodb': ('host', 'port', 'name', 'replicaset'),
    'rethinkdb': ('host', 'port', 'name')
}

_base_database_localmongodb = {
    'host': 'localhost',
    'port': 27017,
    'name': 'bigchain',
    'replicaset': None,
    'login': None,
    'password': None,
}

_base_database_mongodb = {
    'host': 'localhost',
    'port': 27017,
    'name': 'bigchain',
    'replicaset': 'bigchain-rs',
    'login': None,
    'password': None,
}

_database_rethinkdb = {
    'backend': 'rethinkdb',
    'connection_timeout': 5000,
    'max_tries': 3,
}
_database_rethinkdb.update(_base_database_rethinkdb)

_database_mongodb = {
    'backend': 'mongodb',
    'connection_timeout': 5000,
    'max_tries': 3,
    'ssl': False,
    'ca_cert': None,
    'certfile': None,
    'keyfile': None,
    'keyfile_passphrase': None,
    'crlfile': None,
}
_database_mongodb.update(_base_database_mongodb)

_database_localmongodb = {
    'backend': 'localmongodb',
    'connection_timeout': 5000,
    'max_tries': 3,
    'ssl': False,
    'ca_cert': None,
    'certfile': None,
    'keyfile': None,
    'keyfile_passphrase': None,
    'crlfile': None,
}
_database_localmongodb.update(_base_database_localmongodb)

_database_map = {
    'localmongodb': _database_localmongodb,
    'mongodb': _database_mongodb,
    'rethinkdb': _database_rethinkdb
}

config = {
    'server': {
        # Note: this section supports all the Gunicorn settings:
        #       - http://docs.gunicorn.org/en/stable/settings.html
        'bind': 'localhost:9984',
        'loglevel': logging.getLevelName(
            log_config['handlers']['console']['level']).lower(),
        'workers': None,  # if None, the value will be cpu_count * 2 + 1
    },
    'wsserver': {
        'scheme': 'ws',
        'host': 'localhost',
        'port': 9985,
        'advertised_scheme': 'ws',
        'advertised_host': 'localhost',
        'advertised_port': 9985,
    },
    # FIXME: hardcoding to localmongodb for now
    'database': _database_map['localmongodb'],
    'keypair': {
        'public': None,
        'private': None,
    },
    'keyring': [],
    'backlog_reassign_delay': 120,
    'log': {
        'file': log_config['handlers']['file']['filename'],
        'error_file': log_config['handlers']['errors']['filename'],
        'level_console': logging.getLevelName(
            log_config['handlers']['console']['level']).lower(),
        'level_logfile': logging.getLevelName(
            log_config['handlers']['file']['level']).lower(),
        'datefmt_console': log_config['formatters']['console']['datefmt'],
        'datefmt_logfile': log_config['formatters']['file']['datefmt'],
        'fmt_console': log_config['formatters']['console']['format'],
        'fmt_logfile': log_config['formatters']['file']['format'],
        'granular_levels': {},
        'port': log_config['root']['port']
    },
}

# We need to maintain a backup copy of the original config dict in case
# the user wants to reconfigure the node. Check ``bigchaindb.config_utils``
# for more info.
_config = copy.deepcopy(config)
from bigchaindb.core import Bigchain  # noqa
from bigchaindb.version import __version__  # noqa
