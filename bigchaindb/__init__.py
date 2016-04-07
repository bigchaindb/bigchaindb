import copy


config = {
    'server': {
        'bind': '0.0.0.0:5000',
    },
    'database': {
        'host': 'localhost',
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
    'api_endpoint': 'http://localhost:8008/api/v1',
    'consensus_plugin': 'default',
}

# We need to maintain a backup copy of the original config dict in case
# the user wants to reconfigure the node. Check ``bigchaindb.config_utils``
# for more info.
_config = copy.deepcopy(config)
from bigchaindb.core import Bigchain  # noqa

