import logging
from os.path import expanduser, join


DEFAULT_LOG_DIR = expanduser('~')


DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'class': 'logging.Formatter',
            'format': ('[%(asctime)s] [%(levelname)s] (%(name)s) '
                       '%(message)s (%(processName)-10s - pid: %(process)d)'),
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
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(DEFAULT_LOG_DIR, 'bigchaindb.log'),
            'mode': 'w',
            'maxBytes':  209715200,
            'backupCount': 5,
            'formatter': 'file',
            'level': logging.INFO,
        },
        'errors': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(DEFAULT_LOG_DIR, 'bigchaindb-errors.log'),
            'mode': 'w',
            'maxBytes':  209715200,
            'backupCount': 5,
            'formatter': 'file',
            'level': logging.ERROR,
        },
    },
    'loggers': {},
    'root': {
        'level': logging.DEBUG,
        'handlers': ['console', 'file', 'errors'],
    },
}
