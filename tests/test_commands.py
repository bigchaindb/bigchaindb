from argparse import Namespace
from pprint import pprint
import copy

import pytest


@pytest.fixture
def mock_run_configure(monkeypatch):
    from bigchaindb.commands import bigchain
    monkeypatch.setattr(bigchain, 'run_configure', lambda *args, **kwargs: None)


@pytest.fixture
def mock_file_config(monkeypatch):
    from bigchaindb import config_utils
    monkeypatch.setattr(config_utils, 'file_config', lambda *args: None)


@pytest.fixture
def mock_write_config(monkeypatch):
    from bigchaindb import config_utils
    monkeypatch.setattr(config_utils, 'write_config', lambda *args: None)


@pytest.fixture
def mock_db_init_with_existing_db(monkeypatch):
    from bigchaindb import db
    from bigchaindb.exceptions import DatabaseAlreadyExists

    def mockreturn():
        raise DatabaseAlreadyExists

    monkeypatch.setattr(db, 'init', mockreturn)


@pytest.fixture
def mock_processes_start(monkeypatch):
    from bigchaindb.processes import Processes
    monkeypatch.setattr(Processes, 'start', lambda *args: None)


@pytest.fixture
def mock_rethink_db_drop(monkeypatch):
    def mockreturn(dbname):
        class MockDropped(object):
            def run(self, conn):
                return
        return MockDropped()
    monkeypatch.setattr('rethinkdb.db_drop', mockreturn)


@pytest.fixture
def mock_generate_key_pair(monkeypatch):
    monkeypatch.setattr('bigchaindb.crypto.generate_key_pair', lambda: ('privkey', 'pubkey'))


@pytest.fixture
def mock_bigchaindb_backup_config(monkeypatch):
    config = {
        'keypair': {},
        'database': {'host': 'host', 'port': 12345, 'name': 'adbname'},
    }
    monkeypatch.setattr('bigchaindb._config', config)


def test_bigchain_run_start(mock_run_configure, mock_file_config,
                            mock_processes_start, mock_db_init_with_existing_db):
    from bigchaindb.commands.bigchain import run_start
    args = Namespace(config=None, yes=True)
    run_start(args)


def test_bigchain_run_start_assume_yes_create_default_config(monkeypatch, mock_processes_start,
                                                             mock_generate_key_pair, mock_db_init_with_existing_db):
    import bigchaindb
    from bigchaindb.commands.bigchain import run_start
    from bigchaindb import config_utils

    value = {}
    expected_config = copy.deepcopy(bigchaindb._config)
    expected_config['keypair']['public'] = 'pubkey'
    expected_config['keypair']['private'] = 'privkey'

    def mock_write_config(newconfig, filename=None):
        value['return'] = newconfig

    monkeypatch.setattr(config_utils, 'write_config', mock_write_config)
    monkeypatch.setattr(config_utils, 'file_config', lambda x: config_utils.dict_config(value['return']))
    monkeypatch.setattr('os.path.exists', lambda path: False)

    args = Namespace(config=None, yes=True)
    run_start(args)

    assert value['return'] == expected_config


# TODO Please beware, that if debugging, the "-s" switch for pytest will
# interfere with capsys.
# See related issue: https://github.com/pytest-dev/pytest/issues/128
def test_bigchain_show_config(capsys, mock_file_config):
    from bigchaindb import config
    from bigchaindb.commands.bigchain import run_show_config
    args = Namespace(config=None)
    _, _ = capsys.readouterr()
    run_show_config(args)
    output_config, _ = capsys.readouterr()
    pprint(config)
    expected_outout_config, _ = capsys.readouterr()
    assert output_config == expected_outout_config


def test_bigchain_run_init_when_db_exists(mock_file_config, mock_db_init_with_existing_db):
    from bigchaindb.commands.bigchain import run_init
    args = Namespace(config=None)
    run_init(args)


def test_drop_existing_db(mock_file_config, mock_rethink_db_drop):
    from bigchaindb.commands.bigchain import run_drop
    args = Namespace(config=None, yes=True)
    run_drop(args)


def test_run_configure_when_config_exists_and_skipping(monkeypatch):
    from bigchaindb.commands.bigchain import run_configure
    monkeypatch.setattr('os.path.exists', lambda path: True)
    args = Namespace(config='foo', yes=True)
    return_value = run_configure(args, skip_if_exists=True)
    assert return_value is None


# TODO Beware if you are putting breakpoints in there, and using the '-s'
# switch with pytest. It will just hang. Seems related to the monkeypatching of
# input.
def test_run_configure_when_config_does_not_exist(monkeypatch,
                                                  mock_write_config,
                                                  mock_generate_key_pair,
                                                  mock_bigchaindb_backup_config):
    from bigchaindb.commands.bigchain import run_configure
    monkeypatch.setattr('os.path.exists', lambda path: False)
    monkeypatch.setattr('builtins.input', lambda question: '\n')
    args = Namespace(config='foo', yes=True)
    return_value = run_configure(args)
    assert return_value is None
