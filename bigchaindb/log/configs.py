import logging
from os.path import expanduser, join


DEFAULT_LOG_DIR = expanduser('~')

PUBLISHER_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': logging.DEBUG,
    },
}

SUBSCRIBER_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'class': 'logging.Formatter',
            'format': (
                '%(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
            ),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'file': {
            'class': 'logging.Formatter',
            'format': ('[%(asctime)s] [%(levelname)s] (%(name)s) '
                       '%(message)s (%(processName)-10s - pid: %(process)d)'),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'level': logging.INFO,
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': join(DEFAULT_LOG_DIR, 'bigchaindb.log'),
            'mode': 'w',
            'formatter': 'file',
            'level': logging.INFO,
        },
        'errors': {
            'class': 'logging.FileHandler',
            'filename': join(DEFAULT_LOG_DIR, 'bigchaindb-errors.log'),
            'mode': 'w',
            'level': logging.ERROR,
            'formatter': 'file',
        },
    },
    'loggers': {},
    'root': {
        'level': logging.DEBUG,
        'handlers': ['console', 'file', 'errors']
    },
}
