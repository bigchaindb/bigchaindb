import copy
import os

# from functools import reduce
# PORT_NUMBER = reduce(lambda x, y: x * y, map(ord, 'BigchainDB')) % 2**16
# basically, the port number is 9984


config = {
    'server': {
        # Note: this section supports all the Gunicorn settings:
        #       - http://docs.gunicorn.org/en/stable/settings.html
        'bind': 'localhost:9984',
        'workers': None, # if none, the value will be cpu_count * 2 + 1
        'threads': None, # if none, the value will be cpu_count * 2 + 1
    },
    'database': {
        'host': os.environ.get('BIGCHAINDB_DATABASE_HOST', 'localhost'),
        'port': 28015,
        'name': 'bigchain',
    },
    'keypair': {
        'public': None,
        'private': None,
    },
    'keyring': [],
    'statsd': {
        'host': 'localhost',
        'port': 8125,
        'rate': 0.01,
    },
    'api_endpoint': 'http://localhost:9984/api/v1',
    'consensus_plugin': 'default',
}

# We need to maintain a backup copy of the original config dict in case
# the user wants to reconfigure the node. Check ``bigchaindb.config_utils``
# for more info.
_config = copy.deepcopy(config)
from bigchaindb.core import Bigchain  # noqa
from bigchaindb.version import __version__  # noqa
