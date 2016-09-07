import json
from unittest.mock import Mock, patch
from argparse import Namespace
import copy

import pytest
import rethinkdb


@pytest.fixture
def mock_run_configure(monkeypatch):
    from bigchaindb.commands import bigchain
    monkeypatch.setattr(bigchain, 'run_configure', lambda *args, **kwargs: None)


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
    from bigchaindb import processes
    monkeypatch.setattr(processes, 'start', lambda *args: None)


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
        'statsd': {'host': 'host', 'port': 12345, 'rate': 0.1},
        'backlog_reassign_delay': 5
    }
    monkeypatch.setattr('bigchaindb._config', config)


def test_bigchain_run_start(mock_run_configure, mock_processes_start, mock_db_init_with_existing_db):
    from bigchaindb.commands.bigchain import run_start
    args = Namespace(start_rethinkdb=False, config=None, yes=True)
    run_start(args)


@patch('bigchaindb.commands.utils.start_rethinkdb')
def test_bigchain_run_start_with_rethinkdb(mock_start_rethinkdb,
                                           mock_run_configure,
                                           mock_processes_start,
                                           mock_db_init_with_existing_db):
    from bigchaindb.commands.bigchain import run_start
    args = Namespace(start_rethinkdb=True, config=None, yes=True)
    run_start(args)

    mock_start_rethinkdb.assert_called_with()


@pytest.mark.skipif(reason="BigchainDB doesn't support the automatic creation of a config file anymore")
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
    monkeypatch.setattr(config_utils, 'file_config', lambda x: config_utils.set_config(expected_config))
    monkeypatch.setattr('os.path.exists', lambda path: False)

    args = Namespace(config=None, yes=True)
    run_start(args)

    assert value['return'] == expected_config


# TODO Please beware, that if debugging, the "-s" switch for pytest will
# interfere with capsys.
# See related issue: https://github.com/pytest-dev/pytest/issues/128
@pytest.mark.usefixtures('restore_config')
def test_bigchain_show_config(capsys):
    from bigchaindb import config
    from bigchaindb.commands.bigchain import run_show_config

    args = Namespace(config=None)
    _, _ = capsys.readouterr()
    run_show_config(args)
    output_config = json.loads(capsys.readouterr()[0])
    del config['CONFIGURED']
    config['keypair']['private'] = 'x' * 45
    assert output_config == config


def test_bigchain_export_my_pubkey_when_pubkey_set(capsys, monkeypatch):
    from bigchaindb import config
    from bigchaindb.commands.bigchain import run_export_my_pubkey

    args = Namespace(config='dummy')
    # so in run_export_my_pubkey(args) below,
    # filename=args.config='dummy' is passed to autoconfigure().
    # We just assume autoconfigure() works and sets
    # config['keypair']['public'] correctly (tested elsewhere).
    # We force-set config['keypair']['public'] using monkeypatch.
    monkeypatch.setitem(config['keypair'], 'public', 'Charlie_Bucket')
    _, _ = capsys.readouterr()  # has the effect of clearing capsys
    run_export_my_pubkey(args)
    out, err = capsys.readouterr()
    assert out == config['keypair']['public'] + '\n'
    assert out == 'Charlie_Bucket\n'


def test_bigchain_export_my_pubkey_when_pubkey_not_set(monkeypatch):
    from bigchaindb import config
    from bigchaindb.commands.bigchain import run_export_my_pubkey

    args = Namespace(config='dummy')
    monkeypatch.setitem(config['keypair'], 'public', None)
    # assert that run_export_my_pubkey(args) raises SystemExit:
    with pytest.raises(SystemExit) as exc_info:
        run_export_my_pubkey(args)
    # exc_info is an object of class ExceptionInfo
    # https://pytest.org/latest/builtin.html#_pytest._code.ExceptionInfo
    assert exc_info.type == SystemExit
    # exc_info.value is an object of class SystemExit
    # https://docs.python.org/3/library/exceptions.html#SystemExit
    assert exc_info.value.code == \
        "This node's public key wasn't set anywhere so it can't be exported"


def test_bigchain_run_init_when_db_exists(mock_db_init_with_existing_db):
    from bigchaindb.commands.bigchain import run_init
    args = Namespace(config=None)
    run_init(args)


def test_drop_existing_db(mock_rethink_db_drop):
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
    monkeypatch.setattr('builtins.input', lambda: '\n')
    args = Namespace(config='foo', yes=True)
    return_value = run_configure(args)
    assert return_value is None


def test_run_configure_when_config_does_exist(monkeypatch,
                                              mock_write_config,
                                              mock_generate_key_pair,
                                              mock_bigchaindb_backup_config):
    value = {}
    def mock_write_config(newconfig, filename=None):
        value['return'] = newconfig

    from bigchaindb.commands.bigchain import run_configure
    monkeypatch.setattr('os.path.exists', lambda path: True)
    monkeypatch.setattr('builtins.input', lambda: '\n')
    monkeypatch.setattr('bigchaindb.config_utils.write_config', mock_write_config)

    args = Namespace(config='foo', yes=None)
    run_configure(args)
    assert value == {}


@patch('subprocess.Popen')
def test_start_rethinkdb_returns_a_process_when_successful(mock_popen):
    from bigchaindb.commands import utils
    mock_popen.return_value = Mock(stdout=['Server ready'])
    assert utils.start_rethinkdb() is mock_popen.return_value


@patch('subprocess.Popen')
def test_start_rethinkdb_exits_when_cannot_start(mock_popen):
    from bigchaindb import exceptions
    from bigchaindb.commands import utils
    mock_popen.return_value = Mock(stdout=['Nopety nope'])
    with pytest.raises(exceptions.StartupError):
        utils.start_rethinkdb()


@patch('rethinkdb.ast.Table.reconfigure')
def test_set_shards(mock_reconfigure, monkeypatch, b):
    from bigchaindb.commands.bigchain import run_set_shards

    # this will mock the call to retrieve the database config
    # we will set it to return one replica
    def mockreturn_one_replica(self, conn):
        return {'shards': [{'replicas': [1]}]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_one_replica)
    args = Namespace(num_shards=3)
    run_set_shards(args)
    mock_reconfigure.assert_called_with(replicas=1, shards=3)

    # this will mock the call to retrieve the database config
    # we will set it to return three replica
    def mockreturn_three_replicas(self, conn):
        return {'shards': [{'replicas': [1, 2, 3]}]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_three_replicas)
    run_set_shards(args)
    mock_reconfigure.assert_called_with(replicas=3, shards=3)


@patch('logging.Logger.warn')
def test_set_shards_raises_exception(mock_log, monkeypatch, b):
    from bigchaindb.commands.bigchain import run_set_shards

    # test that we are correctly catching the exception
    def mock_raise(*args, **kwargs):
        raise rethinkdb.ReqlOpFailedError('')

    def mockreturn_one_replica(self, conn):
        return {'shards': [{'replicas': [1]}]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_one_replica)
    monkeypatch.setattr(rethinkdb.ast.Table, 'reconfigure', mock_raise)

    args = Namespace(num_shards=3)
    run_set_shards(args)

    assert mock_log.called


@patch('rethinkdb.ast.Table.reconfigure')
def test_set_replicas(mock_reconfigure, monkeypatch, b):
    from bigchaindb.commands.bigchain import run_set_replicas

    # this will mock the call to retrieve the database config
    # we will set it to return two shards
    def mockreturn_two_shards(self, conn):
        return {'shards': [1, 2]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_two_shards)
    args = Namespace(num_replicas=2)
    run_set_replicas(args)
    mock_reconfigure.assert_called_with(replicas=2, shards=2)

    # this will mock the call to retrieve the database config
    # we will set it to return three shards
    def mockreturn_three_shards(self, conn):
        return {'shards': [1, 2, 3]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_three_shards)
    run_set_replicas(args)
    mock_reconfigure.assert_called_with(replicas=2, shards=3)


@patch('logging.Logger.warn')
def test_set_replicas_raises_exception(mock_log, monkeypatch, b):
    from bigchaindb.commands.bigchain import run_set_replicas

    # test that we are correctly catching the exception
    def mock_raise(*args, **kwargs):
        raise rethinkdb.ReqlOpFailedError('')

    def mockreturn_two_shards(self, conn):
        return {'shards': [1, 2]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_two_shards)
    monkeypatch.setattr(rethinkdb.ast.Table, 'reconfigure', mock_raise)

    args = Namespace(num_replicas=2)
    run_set_replicas(args)

    assert mock_log.called
