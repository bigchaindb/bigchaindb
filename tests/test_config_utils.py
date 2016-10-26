import copy
from unittest.mock import mock_open, patch

import pytest

import bigchaindb


ORIGINAL_CONFIG = copy.deepcopy(bigchaindb._config)


@pytest.fixture
def ignore_local_config_file(monkeypatch):
    """
    This fixture's purpose is to override the one under
    :module:`tests/conftest.py` so that the original behaviour of
    :func:`bigchaindb.config_utils.file_config` is restored, so that it can be
    tested.

    """
    from bigchaindb.config_utils import file_config
    monkeypatch.setattr('bigchaindb.config_utils.file_config', file_config)


@pytest.fixture(scope='function', autouse=True)
def clean_config(monkeypatch):
    monkeypatch.setattr('bigchaindb.config', copy.deepcopy(ORIGINAL_CONFIG))


def test_bigchain_instance_is_initialized_when_conf_provided():
    from bigchaindb import config_utils
    assert 'CONFIGURED' not in bigchaindb.config

    config_utils.set_config({'keypair': {'public': 'a', 'private': 'b'}})

    assert bigchaindb.config['CONFIGURED'] is True
    b = bigchaindb.Bigchain()

    assert b.me
    assert b.me_private


def test_bigchain_instance_raises_when_not_configured(monkeypatch):
    from bigchaindb import config_utils
    from bigchaindb.common import exceptions
    assert 'CONFIGURED' not in bigchaindb.config

    # We need to disable ``bigchaindb.config_utils.autoconfigure`` to avoid reading
    # from existing configurations
    monkeypatch.setattr(config_utils, 'autoconfigure', lambda: 0)

    with pytest.raises(exceptions.KeypairNotFoundException):
        bigchaindb.Bigchain()


def test_map_leafs_iterator():
    from bigchaindb import config_utils

    mapping = {
        'a': {'b': {'c': 1},
              'd': {'z': 44}},
        'b': {'d': 2},
        'c': 3
    }

    result = config_utils.map_leafs(lambda x, path: x * 2, mapping)
    assert result == {
        'a': {'b': {'c': 2},
              'd': {'z': 88}},
        'b': {'d': 4},
        'c': 6
    }

    result = config_utils.map_leafs(lambda x, path: path, mapping)
    assert result == {
        'a': {'b': {'c': ['a', 'b', 'c']},
              'd': {'z': ['a', 'd', 'z']}},
        'b': {'d': ['b', 'd']},
        'c': ['c']
    }


def test_update_types():
    from bigchaindb import config_utils

    raw = {
        'a_string': 'test',
        'an_int': '42',
        'a_float': '3.14',
        'a_list': 'a:b:c',
    }

    reference = {
        'a_string': 'test',
        'an_int': 42,
        'a_float': 3.14,
        'a_list': ['a', 'b', 'c'],
    }

    result = config_utils.update_types(raw, reference)
    assert result == reference


def test_env_config(monkeypatch):
    monkeypatch.setattr('os.environ', {'BIGCHAINDB_DATABASE_HOST': 'test-host',
                                       'BIGCHAINDB_DATABASE_PORT': 'test-port'})

    from bigchaindb import config_utils

    result = config_utils.env_config({'database': {'host': None, 'port': None}})
    expected = {'database': {'host': 'test-host', 'port': 'test-port'}}

    assert result == expected


def test_autoconfigure_read_both_from_file_and_env(monkeypatch):
    file_config = {
        'database': {'host': 'test-host'},
        'backlog_reassign_delay': 5
    }
    monkeypatch.setattr('bigchaindb.config_utils.file_config', lambda *args, **kwargs: file_config)
    monkeypatch.setattr('os.environ', {'BIGCHAINDB_DATABASE_NAME': 'test-dbname',
                                       'BIGCHAINDB_DATABASE_PORT': '4242',
                                       'BIGCHAINDB_API_ENDPOINT': 'api://ipa',
                                       'BIGCHAINDB_SERVER_BIND': '1.2.3.4:56',
                                       'BIGCHAINDB_KEYRING': 'pubkey_0:pubkey_1:pubkey_2'})

    import bigchaindb
    from bigchaindb import config_utils
    config_utils.autoconfigure()

    assert bigchaindb.config == {
        'CONFIGURED': True,
        'server': {
            'bind': '1.2.3.4:56',
            'workers': None,
            'threads': None,
        },
        'database': {
            'host': 'test-host',
            'port': 4242,
            'name': 'test-dbname',
        },
        'keypair': {
            'public': None,
            'private': None,
        },
        'keyring': ['pubkey_0', 'pubkey_1', 'pubkey_2'],
        'statsd': {
            'host': 'localhost',
            'port': 8125,
            'rate': 0.01,
        },
        'api_endpoint': 'api://ipa',
        'backlog_reassign_delay': 5
    }


def test_autoconfigure_env_precedence(monkeypatch):
    file_config = {
        'database': {'host': 'test-host', 'name': 'bigchaindb', 'port': 28015}
    }
    monkeypatch.setattr('bigchaindb.config_utils.file_config', lambda *args, **kwargs: file_config)
    monkeypatch.setattr('os.environ', {'BIGCHAINDB_DATABASE_NAME': 'test-dbname',
                                       'BIGCHAINDB_DATABASE_PORT': '4242',
                                       'BIGCHAINDB_SERVER_BIND': 'localhost:9985'})

    import bigchaindb
    from bigchaindb import config_utils
    config_utils.autoconfigure()

    assert bigchaindb.config['CONFIGURED']
    assert bigchaindb.config['database']['host'] == 'test-host'
    assert bigchaindb.config['database']['name'] == 'test-dbname'
    assert bigchaindb.config['database']['port'] == 4242
    assert bigchaindb.config['server']['bind'] == 'localhost:9985'


def test_update_config(monkeypatch):
    import bigchaindb
    from bigchaindb import config_utils

    file_config = {
        'database': {'host': 'test-host', 'name': 'bigchaindb', 'port': 28015}
    }
    monkeypatch.setattr('bigchaindb.config_utils.file_config', lambda *args, **kwargs: file_config)
    config_utils.autoconfigure(config=file_config)

    # update configuration, retaining previous changes
    config_utils.update_config({'database': {'port': 28016, 'name': 'bigchaindb_other'}})

    assert bigchaindb.config['database']['host'] == 'test-host'
    assert bigchaindb.config['database']['name'] == 'bigchaindb_other'
    assert bigchaindb.config['database']['port'] == 28016


def test_file_config():
    from bigchaindb.config_utils import file_config, CONFIG_DEFAULT_PATH
    with patch('builtins.open', mock_open(read_data='{}')) as m:
        config = file_config()
    m.assert_called_once_with(CONFIG_DEFAULT_PATH)
    assert config == {}


def test_invalid_file_config():
    from bigchaindb.config_utils import file_config
    from bigchaindb.common import exceptions
    with patch('builtins.open', mock_open(read_data='{_INVALID_JSON_}')):
        with pytest.raises(exceptions.ConfigurationError):
            file_config()


def test_write_config():
    from bigchaindb.config_utils import write_config, CONFIG_DEFAULT_PATH
    m = mock_open()
    with patch('builtins.open', m):
        write_config({})
    m.assert_called_once_with(CONFIG_DEFAULT_PATH, 'w')
    handle = m()
    handle.write.assert_called_once_with('{}')
