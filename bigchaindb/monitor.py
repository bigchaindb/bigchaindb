import statsd
from os import getppid
from platform import node

class Monitor(statsd.StatsClient):
    def __init__(self, *args, **kwargs):
        if not kwargs:
            kwargs = {}
        if not kwargs.get('prefix'):
            kwargs['prefix'] = '{hostname}_{pid}.'.format(hostname=node(), pid=getppid())
        super().__init__(*args, **kwargs)
