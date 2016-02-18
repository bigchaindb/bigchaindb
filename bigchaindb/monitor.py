import statsd
from platform import node

class Monitor(statsd.StatsClient):
    def __init__(self, *args, **kwargs):
        if not kwargs:
            kwargs = {}
        if not kwargs.get('prefix'):
            kwargs['prefix'] = '{hostname}.'.format(hostname=node())
        super().__init__(*args, **kwargs)
