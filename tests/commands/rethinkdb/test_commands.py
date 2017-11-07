import pytest
import rethinkdb

from unittest.mock import Mock, patch
from argparse import Namespace


@patch('bigchaindb.commands.utils.start_rethinkdb', return_value=Mock())
def test_bigchain_run_start_with_rethinkdb(mock_start_rethinkdb,
                                           mock_run_configure,
                                           mock_processes_start,
                                           mock_db_init_with_existing_db,
                                           mocked_setup_logging):
    from bigchaindb import config
    from bigchaindb.commands.bigchaindb import run_start
    args = Namespace(start_rethinkdb=True, allow_temp_keypair=False, config=None, yes=True,
                     skip_initialize_database=False)
    run_start(args)

    mock_start_rethinkdb.assert_called_with()
    mocked_setup_logging.assert_called_once_with(user_log_config=config['log'])


@patch('subprocess.Popen')
def test_start_rethinkdb_returns_a_process_when_successful(mock_popen):
    from bigchaindb.commands import utils
    mock_popen.return_value = Mock(stdout=[
        'Listening for client driver 1234',
        'Server ready'])
    assert utils.start_rethinkdb() is mock_popen.return_value


@patch('subprocess.Popen')
def test_start_rethinkdb_exits_when_cannot_start(mock_popen):
    from bigchaindb.common import exceptions
    from bigchaindb.commands import utils
    mock_popen.return_value = Mock(stdout=['Nopety nope'])
    with pytest.raises(exceptions.StartupError):
        utils.start_rethinkdb()


@patch('rethinkdb.ast.Table.reconfigure')
def test_set_shards(mock_reconfigure, monkeypatch, b):
    from bigchaindb.commands.bigchaindb import run_set_shards

    # this will mock the call to retrieve the database config
    # we will set it to return one replica
    def mockreturn_one_replica(self, conn):
        return {'shards': [{'replicas': [1]}]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_one_replica)
    args = Namespace(num_shards=3, config=None)
    run_set_shards(args)
    mock_reconfigure.assert_called_with(replicas=1, shards=3, dry_run=False)

    # this will mock the call to retrieve the database config
    # we will set it to return three replica
    def mockreturn_three_replicas(self, conn):
        return {'shards': [{'replicas': [1, 2, 3]}]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_three_replicas)
    run_set_shards(args)
    mock_reconfigure.assert_called_with(replicas=3, shards=3, dry_run=False)


def test_set_shards_raises_exception(monkeypatch, b):
    from bigchaindb.commands.bigchaindb import run_set_shards

    # test that we are correctly catching the exception
    def mock_raise(*args, **kwargs):
        raise rethinkdb.ReqlOpFailedError('')

    def mockreturn_one_replica(self, conn):
        return {'shards': [{'replicas': [1]}]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_one_replica)
    monkeypatch.setattr(rethinkdb.ast.Table, 'reconfigure', mock_raise)

    args = Namespace(num_shards=3, config=None)
    with pytest.raises(SystemExit) as exc:
        run_set_shards(args)
    assert exc.value.args == ('Failed to reconfigure tables.',)


@patch('rethinkdb.ast.Table.reconfigure')
def test_set_replicas(mock_reconfigure, monkeypatch, b):
    from bigchaindb.commands.bigchaindb import run_set_replicas

    # this will mock the call to retrieve the database config
    # we will set it to return two shards
    def mockreturn_two_shards(self, conn):
        return {'shards': [1, 2]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_two_shards)
    args = Namespace(num_replicas=2, config=None)
    run_set_replicas(args)
    mock_reconfigure.assert_called_with(replicas=2, shards=2, dry_run=False)

    # this will mock the call to retrieve the database config
    # we will set it to return three shards
    def mockreturn_three_shards(self, conn):
        return {'shards': [1, 2, 3]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_three_shards)
    run_set_replicas(args)
    mock_reconfigure.assert_called_with(replicas=2, shards=3, dry_run=False)


def test_set_replicas_raises_exception(monkeypatch, b):
    from bigchaindb.commands.bigchaindb import run_set_replicas

    # test that we are correctly catching the exception
    def mock_raise(*args, **kwargs):
        raise rethinkdb.ReqlOpFailedError('')

    def mockreturn_two_shards(self, conn):
        return {'shards': [1, 2]}

    monkeypatch.setattr(rethinkdb.RqlQuery, 'run', mockreturn_two_shards)
    monkeypatch.setattr(rethinkdb.ast.Table, 'reconfigure', mock_raise)

    args = Namespace(num_replicas=2, config=None)
    with pytest.raises(SystemExit) as exc:
        run_set_replicas(args)
    assert exc.value.args == ('Failed to reconfigure tables.',)
