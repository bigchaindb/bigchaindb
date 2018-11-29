# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from argparse import Namespace

import pytest


@pytest.fixture
def mock_run_configure(monkeypatch):
    from bigchaindb.commands import bigchaindb
    monkeypatch.setattr(bigchaindb, 'run_configure', lambda *args, **kwargs: None)


@pytest.fixture
def mock_write_config(monkeypatch):
    from bigchaindb import config_utils
    monkeypatch.setattr(config_utils, 'write_config', lambda *args: None)


@pytest.fixture
def mock_db_init_with_existing_db(monkeypatch):
    from bigchaindb.commands import bigchaindb
    monkeypatch.setattr(bigchaindb, '_run_init', lambda: None)


@pytest.fixture
def mock_processes_start(monkeypatch):
    from bigchaindb import start
    monkeypatch.setattr(start, 'start', lambda *args: None)


@pytest.fixture
def mock_generate_key_pair(monkeypatch):
    monkeypatch.setattr('bigchaindb.common.crypto.generate_key_pair', lambda: ('privkey', 'pubkey'))


@pytest.fixture
def mock_bigchaindb_backup_config(monkeypatch):
    config = {
        'database': {'host': 'host', 'port': 12345, 'name': 'adbname'},
    }
    monkeypatch.setattr('bigchaindb._config', config)


@pytest.fixture
def run_start_args(request):
    param = getattr(request, 'param', {})
    return Namespace(
        config=param.get('config'),
        skip_initialize_database=param.get('skip_initialize_database', False),
    )


@pytest.fixture
def mocked_setup_logging(mocker):
    return mocker.patch(
        'bigchaindb.log.setup_logging',
        autospec=True,
        spec_set=True,
    )
