from logging.handlers import SocketHandler


class TestHttpServerLogger:

    def test_init(self, mocker):
        from bigchaindb.log.configs import (
            DEFAULT_SOCKET_LOGGING_ADDR as expected_socket_address)
        from bigchaindb.log.loggers import HttpServerLogger
        from gunicorn import config
        logger_config = config.Config()
        logger = HttpServerLogger(logger_config)
        assert len(logger.access_log.handlers) == 1
        assert len(logger.error_log.handlers) == 1
        assert isinstance(logger.access_log.handlers[0], SocketHandler)
        assert isinstance(logger.error_log.handlers[0], SocketHandler)
        assert logger.access_log.handlers[0].address == expected_socket_address
        assert logger.error_log.handlers[0].address == expected_socket_address
