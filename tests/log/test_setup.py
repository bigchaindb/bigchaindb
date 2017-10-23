import logging
import pickle
from logging import getLogger
from logging.config import dictConfig
from logging.handlers import SocketHandler

from pytest import fixture, mark, raises


@fixture
def reset_logging_config():
    original_root_logger_level = getLogger().level
    dictConfig({'version': 1, 'root': {'level': 'NOTSET'}})
    yield
    getLogger().setLevel(original_root_logger_level)


@fixture
def mocked_process(mocker):
    return mocker.patch(
        'bigchaindb.log.setup.Process', autospec=True, spec_set=True)


@fixture
def mocked_socket_server(mocker):
    return mocker.patch(
        'bigchaindb.log.setup.LogRecordSocketServer',
        autospec=True,
        spec_set=True,
    )


@fixture
def log_record_dict():
    return {
        'args': None,
        'created': 1489584900.595193,
        'exc_info': None,
        'exc_text': None,
        'filename': 'config_utils.py',
        'funcName': 'autoconfigure',
        'levelname': 'DEBUG',
        'levelno': 10,
        'lineno': 228,
        'module': 'config_utils',
        'msecs': 595.1929092407227,
        'msg': 'System already configured, skipping autoconfiguration',
        'name': 'bigchaindb.config_utils',
        'pathname': '/usr/src/app/bigchaindb/config_utils.py',
        'process': 1981,
        'processName': 'MainProcess',
        'relativeCreated': 398.4854221343994,
        'stack_info': None,
        'thread': 140352503879424,
        'threadName': 'MainThread',
    }


@fixture
def log_record(log_record_dict):
    return logging.makeLogRecord(log_record_dict)


@fixture
def log_record_bytes(log_record_dict):
    return pickle.dumps(log_record_dict)


@mark.usefixtures('reset_logging_config')
def test_setup_logging(mocked_setup_pub_logger, mocked_setup_sub_logger):
    from bigchaindb.log.setup import setup_logging
    setup_logging()
    mocked_setup_pub_logger.assert_called_once_with(logging_port=None)
    mocked_setup_sub_logger.assert_called_once_with(user_log_config=None)


@mark.usefixtures('reset_logging_config')
def test_setup_pub_logger():
    from bigchaindb.log.setup import setup_pub_logger
    from bigchaindb.log.configs import PUBLISHER_LOGGING_CONFIG
    root_logger = getLogger()
    assert root_logger.level == logging.NOTSET
    setup_pub_logger()
    assert root_logger.level == PUBLISHER_LOGGING_CONFIG['root']['level']
    assert root_logger.hasHandlers()
    assert isinstance(root_logger.handlers[0], SocketHandler)


@mark.usefixtures('reset_logging_config')
def test_setup_sub_logger_without_config(mocked_socket_server, mocked_process):
    from bigchaindb.log.setup import setup_sub_logger
    setup_sub_logger()
    root_logger = getLogger()
    assert root_logger.level == logging.NOTSET
    mocked_socket_server.assert_called_once_with()
    mocked_process.assert_called_once_with(
            target=mocked_socket_server.return_value.serve_forever,
            kwargs={'log_config': None},
    )
    mocked_process.return_value.start.assert_called_once_with()


@mark.usefixtures('reset_logging_config')
def test_setup_sub_logger_with_config(mocked_socket_server, mocked_process):
    from bigchaindb.log.setup import setup_sub_logger
    user_log_config = {
        'file': '/var/log/bdb.log',
        'level_console': 'warning',
        'level_logfile': 'info',
        'fmt_console': '[%(levelname)s] (%(name)s) %(message)s',
        'fmt_logfile': '[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s',
        'granular_levels': {
            'bigchaindb.core': 'debug',
        },
    }
    root_logger = getLogger()
    setup_sub_logger(user_log_config=user_log_config)
    assert root_logger.level == logging.NOTSET
    mocked_socket_server.assert_called_once_with()
    mocked_process.assert_called_once_with(
            target=mocked_socket_server.return_value.serve_forever,
            kwargs={'log_config': user_log_config},
    )
    mocked_process.return_value.start.assert_called_once_with()


def test_create_subscriber_logging_config_without_user_given_config():
    from bigchaindb.log.setup import create_subscriber_logging_config
    from bigchaindb.log.configs import SUBSCRIBER_LOGGING_CONFIG
    config = create_subscriber_logging_config()
    assert config == SUBSCRIBER_LOGGING_CONFIG


def test_create_subscriber_logging_config_with_user_given_config():
    from bigchaindb.log.setup import create_subscriber_logging_config
    from bigchaindb.log.configs import (
        SUBSCRIBER_LOGGING_CONFIG as expected_log_config)
    user_log_config = {
        'file': '/var/log/bigchaindb/bdb.log',
        'error_file': '/var/log/bigchaindb/bdb-err.log',
        'level_console': 'warning',
        'level_logfile': 'info',
        'fmt_console': '[%(levelname)s] (%(name)s) %(message)s',
        'fmt_logfile': '[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s',
        'datefmt_console': '%H:%M:%S',
        'datefmt_logfile': '%a, %d %b %Y %H:%M:%S +0000',
        'granular_levels': {
            'bigchaindb.core': 'debug',
        },
    }
    config = create_subscriber_logging_config(user_log_config=user_log_config)
    assert config['root']['level'] == expected_log_config['root']['level']
    assert all(config['loggers'][logger]['level'] == level.upper()
               for logger, level in user_log_config['granular_levels'].items())
    assert len(config) == len(expected_log_config)
    assert config['version'] == expected_log_config['version']
    assert (config['disable_existing_loggers'] ==
            expected_log_config['disable_existing_loggers'])
    assert (config['formatters']['console']['format'] ==
            user_log_config['fmt_console'])
    assert (config['formatters']['file']['format'] ==
            user_log_config['fmt_logfile'])
    assert (config['formatters']['console']['datefmt'] ==
            user_log_config['datefmt_console'])
    assert (config['formatters']['file']['datefmt'] ==
            user_log_config['datefmt_logfile'])
    assert (config['handlers']['console']['level'] ==
            user_log_config['level_console'].upper())
    assert (config['handlers']['file']['level'] ==
            user_log_config['level_logfile'].upper())
    assert config['handlers']['errors']['level'] == logging.ERROR
    assert config['handlers']['file']['filename'] == user_log_config['file']
    assert (config['handlers']['errors']['filename'] ==
            user_log_config['error_file'])
    del config['handlers']['console']['level']
    del config['handlers']['file']['level']
    del config['handlers']['file']['filename']
    del config['formatters']['console']['format']
    del config['formatters']['console']['datefmt']
    del config['formatters']['file']['format']
    del config['formatters']['file']['datefmt']
    del expected_log_config['handlers']['console']['level']
    del expected_log_config['handlers']['file']['level']
    del expected_log_config['handlers']['file']['filename']
    del expected_log_config['formatters']['console']['format']
    del expected_log_config['formatters']['console']['datefmt']
    del expected_log_config['formatters']['file']['format']
    del expected_log_config['formatters']['file']['datefmt']
    assert (config['handlers']['console'] ==
            expected_log_config['handlers']['console'])
    assert (config['handlers']['file'] ==
            expected_log_config['handlers']['file'])
    assert (config['formatters']['console'] ==
            expected_log_config['formatters']['console'])
    assert (config['formatters']['file'] ==
            expected_log_config['formatters']['file'])


def test_normalize_log_level():
    from bigchaindb.common.exceptions import ConfigurationError
    from bigchaindb.log.setup import _normalize_log_level
    with raises(ConfigurationError) as exc:
        _normalize_log_level(2)
    assert exc.value.args == ('Log level must be a string!',)
    assert isinstance(exc.value.__cause__, AttributeError)
    assert exc.value.__cause__.args == (
        "'int' object has no attribute 'upper'",)


class TestLogRecordSocketServer:

    def test_init(self):
        from bigchaindb.log.setup import (LogRecordSocketServer,
                                          LogRecordStreamHandler)
        server = LogRecordSocketServer()
        assert server.allow_reuse_address
        assert server.server_address == (
            '127.0.0.1', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        assert server.RequestHandlerClass == LogRecordStreamHandler
        server.server_close()

    @mark.parametrize('side_effect', (None, KeyboardInterrupt))
    def test_server_forever(self, mocker, side_effect):
        from bigchaindb.log.setup import LogRecordSocketServer
        nocked_create_subscriber_logging_config = mocker.patch(
            'bigchaindb.log.setup.create_subscriber_logging_config',
            autospec=True,
            spec_set=True,
        )
        mocked_dict_config = mocker.patch('bigchaindb.log.setup.dictConfig',
                                          autospec=True, spec_set=True)
        mocked_parent_serve_forever = mocker.patch(
            'bigchaindb.log.setup.ThreadingTCPServer.serve_forever',
            autospec=True,
            spec_set=True,
            side_effect=side_effect,
        )
        server = LogRecordSocketServer()
        with server:
            server.serve_forever()
        nocked_create_subscriber_logging_config.assert_called_once_with(
            user_log_config=None)
        mocked_dict_config.assert_called_once_with(
            nocked_create_subscriber_logging_config.return_value)
        mocked_parent_serve_forever.assert_called_once_with(server,
                                                            poll_interval=0.5)


class TestLogRecordStreamHandler:

    def test_handle(self, mocker, log_record_dict, log_record_bytes):
        from bigchaindb.log.setup import LogRecordStreamHandler

        chunks = [log_record_bytes, b'\x00\x00\x02T']
        mocked_handle_log_record = mocker.patch(
            'bigchaindb.log.setup.LogRecordStreamHandler.handle_log_record',
            autospec=True,
            spec_set=True,
        )

        def mocked_recv(bufsize):
            try:
                return chunks.pop()
            except IndexError:
                return b' '

        request = mocker.patch('socket.socket', autospec=True, spec_set=True)
        request.return_value.recv = mocked_recv
        client_address = ('127.0.0.1', 9020)
        LogRecordStreamHandler(
            request.return_value, client_address, None)
        assert mocked_handle_log_record.called
        assert (mocked_handle_log_record.call_args[0][1].__dict__ ==
                log_record_dict)

    def test_handle_log_record(self, mocker, log_record):
        from bigchaindb.log.setup import LogRecordStreamHandler
        mocker.patch('bigchaindb.log.setup.LogRecordStreamHandler.handle')
        mocked_logger_handle = mocker.patch(
            'bigchaindb.log.setup.logging.Logger.handle',
            autospec=True, spec_set=True)
        request = mocker.patch('socket.socket', autospec=True, spec_set=True)
        client_address = ('127.0.0.1', 9020)
        handler = LogRecordStreamHandler(
            request.return_value, client_address, None)
        handler.handle_log_record(log_record)
        assert log_record in mocked_logger_handle.call_args[0]

    def test_unpickle(self, mocker, log_record_bytes, log_record_dict):
        from bigchaindb.log.setup import LogRecordStreamHandler
        mocker.patch('bigchaindb.log.setup.LogRecordStreamHandler.handle')
        request = mocker.patch('socket.socket', autospec=True, spec_set=True)
        client_address = ('127.0.0.1', 9020)
        handler = LogRecordStreamHandler(
            request.return_value, client_address, None)
        obj = handler.unpickle(log_record_bytes)
        assert obj == log_record_dict

    @mark.parametrize('error', (
        pickle.UnpicklingError, AttributeError, EOFError, TypeError))
    def test_unpickle_error(self, mocker, error):
        from bigchaindb.log.setup import LogRecordStreamHandler
        mocker.patch('bigchaindb.log.setup.LogRecordStreamHandler.handle')
        mocker.patch(
            'bigchaindb.log.setup.pickle.loads',
            autospec=True,
            spec_set=True,
            side_effect=error('msg'),
        )
        request = mocker.patch('socket.socket', autospec=True, spec_set=True)
        client_address = ('127.0.0.1', 9020)
        handler = LogRecordStreamHandler(
            request.return_value, client_address, None)
        obj = handler.unpickle(None)
        assert obj == {
            'msg': '({}) Log handling error: un-pickling failed!'.format(
                error.__name__),
            'exc_info': ('msg',),
            'level': logging.ERROR,
            'func': handler.unpickle.__name__,
        }
