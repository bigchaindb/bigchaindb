from logging import getLogger, StreamHandler
from logging.config import dictConfig

import pytest


# TODO explain why and the link to pytest-catchlog
def reset_loggers(*logger_names):
    for logger_name in logger_names:
        logger = getLogger(logger_name)
        logger.setLevel(0)
        handlers = list(logger.handlers)
        for log_handler in handlers:
            logger.removeHandler(log_handler)
        filters = list(logger.filters)
        for log_filter in filters:
            logger.removeFilter(log_filter)


@pytest.fixture
def reset_logging_config():
    #root_logger_level = getLogger().level
    root_logger_level = 'DEBUG'
    dictConfig({'version': 1, 'root': {'level': 'NOTSET'}})
    yield
    getLogger().setLevel(root_logger_level)


@pytest.mark.usefixtures('reset_logging_config')
def test_setup_logging_without_config():
    from bigchaindb.log.setup import setup_logging
    root_logger = getLogger()
    assert root_logger.level == 0
    setup_logging()
    assert root_logger.level == 20
    assert root_logger.hasHandlers()
    assert isinstance(root_logger.handlers[0], StreamHandler)

"""
@pytest.mark.usefixtures('reset_logging_config')
def test_setup_logging_with_config():
    from bigchaindb.log.setup import setup_logging

    log_config = {
        'level': 'WARNING',
        'granular_levels': {
            'bigchaindb.core': 'DEBUG',
        },
    }
    setup_logging(log_config=log_config)
    root_logger = getLogger()
    bigchaindb_core_logger = getLogger('bigchaindb.core')
    assert root_logger.level == 30
    assert root_logger.hasHandlers()
    assert isinstance(root_logger.handlers[0], StreamHandler)
    assert bigchaindb_core_logger.level == 10
    assert bigchaindb_core_logger.hasHandlers()
    assert bigchaindb_core_logger.parent == root_logger
"""
