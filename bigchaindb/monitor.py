from platform import node

import statsd

import bigchaindb
from bigchaindb import config_utils


class Monitor(statsd.StatsClient):
    """Set up statsd monitoring."""

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
        if 'prefix' not in kwargs:
            kwargs['prefix'] = '{hostname}.'.format(hostname=node())
        if 'host' not in kwargs:
            kwargs['host'] = bigchaindb.config['statsd']['host']
        if 'port' not in kwargs:
            kwargs['port'] = bigchaindb.config['statsd']['port']
        super().__init__(*args, **kwargs)

