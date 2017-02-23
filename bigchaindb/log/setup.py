"""Setup logging."""
import logging
from logging.config import dictConfig


DEFAULT_ROOT_LOG_LEVEL = 'INFO'

# listener config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    # 'formatters': {
    #     'default': {
    #         'class': 'logging.Formatter',
    #         'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
    #     },
    # },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            # 'formatter': 'default',
        },
    },
    #'loggers': {
    #    'bigchaindb.pipelines': {
    #        'handlers': ['console'],
    #    },
    #},
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
}


def setup_logging(log_config=None):
    dictConfig(LOGGING)
    log_config = log_config or {}
    root_level = log_config.get('level', DEFAULT_ROOT_LOG_LEVEL)
    log_levels = log_config.get('granular_levels', {})
    log_levels[''] = root_level
    for logger_name, level in log_levels.items():
        logging.getLogger(logger_name).setLevel(level)
