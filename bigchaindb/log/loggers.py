import logging.handlers

from gunicorn.glogging import Logger

from .configs import DEFAULT_SOCKET_LOGGING_HOST, DEFAULT_SOCKET_LOGGING_PORT


class HttpServerLogger(Logger):
    """Custom logger class for ``gunicorn`` logs.

    Meant for internal usage only, to set the ``logger_class``
    configuration setting on gunicorn.

    """
    def setup(self, cfg):
        """Setup the gunicorn access and error loggers. This overrides
        the parent method. Its main goal is to simply pipe all the logs to
        the TCP socket used througout BigchainDB.

        Args:
            cfg (:obj:`gunicorn.config.Config`): Gunicorn configuration
                object. *Ignored*.

        """
        log_cfg = self.cfg.env_orig.get('custom_log_config', {})
        self.log_port = log_cfg.get('port', DEFAULT_SOCKET_LOGGING_PORT)

        self._set_socklog_handler(self.error_log)
        self._set_socklog_handler(self.access_log)

    def _set_socklog_handler(self, log):
        socket_handler = logging.handlers.SocketHandler(
            DEFAULT_SOCKET_LOGGING_HOST, self.log_port)
        socket_handler._gunicorn = True
        log.addHandler(socket_handler)
