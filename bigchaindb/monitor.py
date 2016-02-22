import statsd
from platform import node

import bigchaindb
from bigchaindb import config_utils

class Monitor(statsd.StatsClient):
    """Set up statsd monitoring

    """
    def __init__(self, *args, **kwargs):
        """Overrides statsd client, fixing prefix to messages and loading configuration

        Args:
            *args: arguments (identical to Statsclient)
            **kwargs: keyword arguments (identical to Statsclient)
        """
        config_utils.autoconfigure()

        if not kwargs:
            kwargs = {}

        # set prefix, parameters from configuration file
        if not kwargs.get('prefix'):
            kwargs['prefix'] = '{hostname}.'.format(hostname=node())
        if not kwargs.get('host'):
            kwargs['host'] = bigchaindb.config['statsd']['host']
        if not kwargs.get('port'):
            kwargs['port'] = bigchaindb.config['statsd']['port']
        super().__init__(*args, **kwargs)
