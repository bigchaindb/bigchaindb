"""Setup logging."""
from copy import deepcopy
import logging
from logging.config import dictConfig
import logging.handlers
import pickle
from socketserver import StreamRequestHandler, ThreadingTCPServer
import struct
import sys
from multiprocessing import Process

from .configs import (
    DEFAULT_SOCKET_LOGGING_HOST,
    DEFAULT_SOCKET_LOGGING_PORT,
    PUBLISHER_LOGGING_CONFIG,
    SUBSCRIBER_LOGGING_CONFIG,
)
from bigchaindb.common.exceptions import ConfigurationError


def _normalize_log_level(level):
    try:
        return level.upper()
    except AttributeError as exc:
        raise ConfigurationError('Log level must be a string!') from exc


def setup_pub_logger(logging_port=None):
    logging_port = logging_port or DEFAULT_SOCKET_LOGGING_PORT

    dictConfig(PUBLISHER_LOGGING_CONFIG)
    socket_handler = logging.handlers.SocketHandler(
        DEFAULT_SOCKET_LOGGING_HOST, logging_port)
    socket_handler.setLevel(logging.DEBUG)
    logger = logging.getLogger()
    logger.addHandler(socket_handler)


def setup_sub_logger(*, user_log_config=None):
    kwargs = {}
    log_port = user_log_config.get('port') if user_log_config is not None else None

    if log_port is not None:
        kwargs['port'] = log_port

    server = LogRecordSocketServer(**kwargs)
    with server:
        server_proc = Process(
            target=server.serve_forever,
            kwargs={'log_config': user_log_config},
        )
        server_proc.start()


def setup_logging(*, user_log_config=None):
    port = user_log_config.get('port') if user_log_config is not None else None
    setup_pub_logger(logging_port=port)
    setup_sub_logger(user_log_config=user_log_config)


def create_subscriber_logging_config(*, user_log_config=None):  # noqa: C901
    sub_log_config = deepcopy(SUBSCRIBER_LOGGING_CONFIG)

    if not user_log_config:
        return sub_log_config

    if 'file' in user_log_config:
        filename = user_log_config['file']
        sub_log_config['handlers']['file']['filename'] = filename

    if 'error_file' in user_log_config:
        error_filename = user_log_config['error_file']
        sub_log_config['handlers']['errors']['filename'] = error_filename

    if 'level_console' in user_log_config:
        level = _normalize_log_level(user_log_config['level_console'])
        sub_log_config['handlers']['console']['level'] = level

    if 'level_logfile' in user_log_config:
        level = _normalize_log_level(user_log_config['level_logfile'])
        sub_log_config['handlers']['file']['level'] = level

    if 'fmt_console' in user_log_config:
        fmt = user_log_config['fmt_console']
        sub_log_config['formatters']['console']['format'] = fmt

    if 'fmt_logfile' in user_log_config:
        fmt = user_log_config['fmt_logfile']
        sub_log_config['formatters']['file']['format'] = fmt

    if 'datefmt_console' in user_log_config:
        fmt = user_log_config['datefmt_console']
        sub_log_config['formatters']['console']['datefmt'] = fmt

    if 'datefmt_logfile' in user_log_config:
        fmt = user_log_config['datefmt_logfile']
        sub_log_config['formatters']['file']['datefmt'] = fmt

    log_levels = user_log_config.get('granular_levels', {})

    for logger_name, level in log_levels.items():
        level = _normalize_log_level(level)
        try:
            sub_log_config['loggers'][logger_name]['level'] = level
        except KeyError:
            sub_log_config['loggers'][logger_name] = {'level': level}

    return sub_log_config


class LogRecordStreamHandler(StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unpickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handle_log_record(record)

    def unpickle(self, data):
        try:
            return pickle.loads(data)
        except (pickle.UnpicklingError,
                AttributeError, EOFError, TypeError) as exc:
            return {
                'msg': '({}) Log handling error: un-pickling failed!'.format(
                    exc.__class__.__name__),
                'exc_info': exc.args,
                'level': logging.ERROR,
                'func': self.unpickle.__name__,
            }

    def handle_log_record(self, record):
        logger = logging.getLogger(record.name)
        logger.handle(record)


class LogRecordSocketServer(ThreadingTCPServer):
    """
    Simple TCP socket-based logging server.

    """
    allow_reuse_address = True

    def __init__(self,
                 host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        super().__init__((host, port), handler)

    def serve_forever(self, *, poll_interval=0.5, log_config=None):
        sub_logging_config = create_subscriber_logging_config(
            user_log_config=log_config)
        dictConfig(sub_logging_config)
        try:
            super().serve_forever(poll_interval=poll_interval)
        except KeyboardInterrupt:
            pass


# NOTE: Because the context manager is only available
# from 3.6 and up, we add it for lower versions.
if sys.version_info < (3, 6):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.server_close()

    LogRecordSocketServer.__enter__ = __enter__
    LogRecordSocketServer.__exit__ = __exit__
