from logging import getLogger, StreamHandler


# TODO explain why and the link to pytest-catchlog
def reset_root_logger():
    root_logger = getLogger()
    if root_logger.hasHandlers():
        for log_handler in root_logger.handlers:
            root_logger.removeHandler(log_handler)
    for log_filter in root_logger.filters:
        root_logger.removeFilter(log_filter)


def test_setup():
    from bigchaindb.log.setup import setup_logging

    # TODO explain why
    reset_root_logger()

    root_logger = getLogger()
    assert root_logger.level == 0
    assert not root_logger.hasHandlers()
    setup_logging()
    assert root_logger.level == 20
    assert root_logger.hasHandlers()
    assert isinstance(root_logger.handlers[0], StreamHandler)
