from logging import getLogger, StreamHandler


# TODO explain why and the link to pytest-catchlog
def reset_loggers(*logger_names):
    for logger_name in logger_names:
        logger = getLogger(logger_name)
        logger.setLevel(0)
        if logger.hasHandlers():
            for log_handler in logger.handlers:
                logger.removeHandler(log_handler)
        for log_filter in logger.filters:
            logger.removeFilter(log_filter)


def test_setup_logging_without_config():
    from bigchaindb.log.setup import setup_logging

    # TODO explain why
    reset_loggers('')

    root_logger = getLogger()
    assert root_logger.level == 0
    assert not root_logger.hasHandlers()
    setup_logging()
    assert root_logger.level == 20
    assert root_logger.hasHandlers()
    assert isinstance(root_logger.handlers[0], StreamHandler)


def test_setup_logging_with_config():
    from bigchaindb.log.setup import setup_logging

    # TODO explain why
    reset_loggers('', 'bigchaindb.core')
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
