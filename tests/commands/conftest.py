from argparse import Namespace

import pytest


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
    from bigchaindb.commands import bigchain
    monkeypatch.setattr(bigchain, '_run_init', lambda: None)


@pytest.fixture
def mock_processes_start(monkeypatch):
    from bigchaindb import processes
    monkeypatch.setattr(processes, 'start', lambda *args: None)


@pytest.fixture
def mock_generate_key_pair(monkeypatch):
    monkeypatch.setattr('bigchaindb.common.crypto.generate_key_pair', lambda: ('privkey', 'pubkey'))


@pytest.fixture
def mock_bigchaindb_backup_config(monkeypatch):
    config = {
        'keypair': {},
        'database': {'host': 'host', 'port': 12345, 'name': 'adbname'},
        'backlog_reassign_delay': 5
    }
    monkeypatch.setattr('bigchaindb._config', config)


@pytest.fixture
def run_start_args(request):
    param = getattr(request, 'param', {})
    return Namespace(
        config=param.get('config'),
        start_rethinkdb=param.get('start_rethinkdb', False),
        allow_temp_keypair=param.get('allow_temp_keypair', False),
    )


@pytest.fixture
def mocked_setup_logging(mocker):
    return mocker.patch(
        'bigchaindb.commands.utils.setup_logging',
        autospec=True,
        spec_set=True,
    )
