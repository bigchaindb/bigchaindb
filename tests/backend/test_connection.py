from copy import copy

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_imported_connection_cls(monkeypatch):
    from bigchaindb import config
    monkeypatch.setattr('bigchaindb.backend.connection.BACKENDS',
                        {config['database']['backend']:
                         'bigchaindb.backend.mock.MockDBConnection'})

    with patch('bigchaindb.backend.connection.import_module') as mock_import:
        # Set up mocks for imported connection lib
        mock_connection_cls = Mock()
        mock_connection_module = Mock()
        mock_connection_module.MockDBConnection = mock_connection_cls
        mock_import.return_value = mock_connection_module

        yield mock_connection_cls


def test_get_connection_uses_current_configuration1(mock_imported_connection_cls):
    from bigchaindb import config
    from bigchaindb.backend import connect
    expected_args = copy(config['database'])
    del expected_args['backend']

    connect()
    mock_imported_connection_cls.assert_called_once_with(**expected_args)


def test_get_connection_overrides_current_configuration_from_kwargs(mock_imported_connection_cls):
    from bigchaindb import config
    from bigchaindb.backend import connect
    mock_port = 123
    mock_hostname = 'hostname'
    mock_extra_value = 'extra'

    expected_args = copy(config['database'])
    expected_args.update({
        'port': mock_port,
        'host': mock_hostname,
        'extra_value': mock_extra_value,
    })
    del expected_args['backend']

    connect(port=mock_port, host=mock_hostname, extra_value=mock_extra_value)
    mock_imported_connection_cls.assert_called_once_with(**expected_args)


def test_get_connection_raises_a_configuration_error(monkeypatch):
    from bigchaindb.common.exceptions import ConfigurationError
    from bigchaindb.backend import connect

    with pytest.raises(ConfigurationError):
        connect(backend='msaccess', host='localhost', port='1337', extra='mydb')

    with pytest.raises(ConfigurationError):
        # We need to force a misconfiguration here
        monkeypatch.setattr('bigchaindb.backend.connection.BACKENDS',
                            {'catsandra':
                             'bigchaindb.backend.meowmeow.CatsandraConnection'})

        connect(backend='catsandra', host='localhost', port='1337', extra='mydb')
