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
