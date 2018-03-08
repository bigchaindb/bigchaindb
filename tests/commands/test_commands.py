import json
from unittest.mock import Mock, patch
from argparse import Namespace

import pytest


@pytest.mark.tendermint
def test_make_sure_we_dont_remove_any_command():
    # thanks to: http://stackoverflow.com/a/18161115/597097
    from bigchaindb.commands.bigchaindb import create_parser

    parser = create_parser()

    assert parser.parse_args(['configure', 'localmongodb']).command
    assert parser.parse_args(['show-config']).command
    assert parser.parse_args(['init']).command
    assert parser.parse_args(['drop']).command
    assert parser.parse_args(['start']).command


@pytest.mark.tendermint
@patch('bigchaindb.commands.utils.start')
def test_main_entrypoint(mock_start):
    from bigchaindb.commands.bigchaindb import main
    main()

    assert mock_start.called


def test_bigchain_run_start(mock_run_configure,
                            mock_processes_start,
                            mock_db_init_with_existing_db,
                            mocked_setup_logging):
    from bigchaindb import config
    from bigchaindb.commands.bigchaindb import run_start
    args = Namespace(config=None, yes=True,
                     skip_initialize_database=False)
    run_start(args)
    mocked_setup_logging.assert_called_once_with(user_log_config=config['log'])


# TODO Please beware, that if debugging, the "-s" switch for pytest will
# interfere with capsys.
# See related issue: https://github.com/pytest-dev/pytest/issues/128
@pytest.mark.tendermint
@pytest.mark.usefixtures('ignore_local_config_file')
def test_bigchain_show_config(capsys):
    from bigchaindb.commands.bigchaindb import run_show_config

    args = Namespace(config=None)
    _, _ = capsys.readouterr()
    run_show_config(args)
    output_config = json.loads(capsys.readouterr()[0])
    # Note: This test passed previously because we were always
    # using the default configuration parameters, but since we
    # are running with docker-compose now and expose parameters like
    # BIGCHAINDB_SERVER_BIND, BIGCHAINDB_WSSERVER_HOST, BIGCHAINDB_WSSERVER_ADVERTISED_HOST
    # the default comparison fails i.e. when config is imported at the beginning the
    # dict returned is different that what is expected after run_show_config
    # and run_show_config updates the bigchaindb.config
    from bigchaindb import config
    del config['CONFIGURED']
    config['keypair']['private'] = 'x' * 45
    assert output_config == config


@pytest.mark.tendermint
def test_bigchain_run_init_when_db_exists(mocker, capsys):
    from bigchaindb.commands.bigchaindb import run_init
    from bigchaindb.common.exceptions import DatabaseAlreadyExists
    init_db_mock = mocker.patch(
        'bigchaindb.commands.bigchaindb.schema.init_database',
        autospec=True,
        spec_set=True,
    )
    init_db_mock.side_effect = DatabaseAlreadyExists
    args = Namespace(config=None)
    run_init(args)
    output_message = capsys.readouterr()[1]
    print(output_message)
    assert output_message == (
        'The database already exists.\n'
        'If you wish to re-initialize it, first drop it.\n'
    )


@pytest.mark.tendermint
def test__run_init(mocker):
    from bigchaindb.commands.bigchaindb import _run_init
    bigchain_mock = mocker.patch(
        'bigchaindb.commands.bigchaindb.bigchaindb.Bigchain')
    init_db_mock = mocker.patch(
        'bigchaindb.commands.bigchaindb.schema.init_database',
        autospec=True,
        spec_set=True,
    )
    _run_init()
    bigchain_mock.assert_called_once_with()
    init_db_mock.assert_called_once_with(
        connection=bigchain_mock.return_value.connection)
    bigchain_mock.return_value.create_genesis_block.assert_called_once_with()


@pytest.mark.tendermint
@patch('bigchaindb.backend.schema.drop_database')
def test_drop_db_when_assumed_yes(mock_db_drop):
    from bigchaindb.commands.bigchaindb import run_drop
    args = Namespace(config=None, yes=True)

    run_drop(args)
    assert mock_db_drop.called


@pytest.mark.tendermint
@patch('bigchaindb.backend.schema.drop_database')
def test_drop_db_when_interactive_yes(mock_db_drop, monkeypatch):
    from bigchaindb.commands.bigchaindb import run_drop
    args = Namespace(config=None, yes=False)
    monkeypatch.setattr(
        'bigchaindb.commands.bigchaindb.input_on_stderr', lambda x: 'y')

    run_drop(args)
    assert mock_db_drop.called


@pytest.mark.tendermint
@patch('bigchaindb.backend.schema.drop_database')
def test_drop_db_when_db_does_not_exist(mock_db_drop, capsys):
    from bigchaindb import config
    from bigchaindb.commands.bigchaindb import run_drop
    from bigchaindb.common.exceptions import DatabaseDoesNotExist
    args = Namespace(config=None, yes=True)
    mock_db_drop.side_effect = DatabaseDoesNotExist

    run_drop(args)
    output_message = capsys.readouterr()[1]
    assert output_message == "Cannot drop '{name}'. The database does not exist.\n".format(
        name=config['database']['name'])


@pytest.mark.tendermint
@patch('bigchaindb.backend.schema.drop_database')
def test_drop_db_does_not_drop_when_interactive_no(mock_db_drop, monkeypatch):
    from bigchaindb.commands.bigchaindb import run_drop
    args = Namespace(config=None, yes=False)
    monkeypatch.setattr(
        'bigchaindb.commands.bigchaindb.input_on_stderr', lambda x: 'n')

    run_drop(args)
    assert not mock_db_drop.called


# TODO Beware if you are putting breakpoints in there, and using the '-s'
# switch with pytest. It will just hang. Seems related to the monkeypatching of
# input_on_stderr.
@pytest.mark.tendermint
def test_run_configure_when_config_does_not_exist(monkeypatch,
                                                  mock_write_config,
                                                  mock_generate_key_pair,
                                                  mock_bigchaindb_backup_config):
    from bigchaindb.commands.bigchaindb import run_configure
    monkeypatch.setattr('os.path.exists', lambda path: False)
    monkeypatch.setattr('builtins.input', lambda: '\n')
    args = Namespace(config=None, backend='localmongodb', yes=True)
    return_value = run_configure(args)
    assert return_value is None


@pytest.mark.tendermint
def test_run_configure_when_config_does_exist(monkeypatch,
                                              mock_write_config,
                                              mock_generate_key_pair,
                                              mock_bigchaindb_backup_config):
    value = {}

    def mock_write_config(newconfig, filename=None):
        value['return'] = newconfig

    from bigchaindb.commands.bigchaindb import run_configure
    monkeypatch.setattr('os.path.exists', lambda path: True)
    monkeypatch.setattr('builtins.input', lambda: '\n')
    monkeypatch.setattr(
        'bigchaindb.config_utils.write_config', mock_write_config)

    args = Namespace(config=None, yes=None)
    run_configure(args)
    assert value == {}


@pytest.mark.tendermint
@pytest.mark.parametrize('backend', (
    'localmongodb',
))
def test_run_configure_with_backend(backend, monkeypatch, mock_write_config):
    import bigchaindb
    from bigchaindb.commands.bigchaindb import run_configure

    value = {}

    def mock_write_config(new_config, filename=None):
        value['return'] = new_config

    monkeypatch.setattr('os.path.exists', lambda path: False)
    monkeypatch.setattr('builtins.input', lambda: '\n')
    monkeypatch.setattr('bigchaindb.config_utils.write_config',
                        mock_write_config)

    args = Namespace(config=None, backend=backend, yes=True)
    expected_config = bigchaindb.config
    run_configure(args)

    # update the expected config with the correct backend and keypair
    backend_conf = getattr(bigchaindb, '_database_' + backend)
    expected_config.update({'database': backend_conf,
                            'keypair': value['return']['keypair']})

    assert value['return'] == expected_config


def test_run_start_when_db_already_exists(mocker,
                                          monkeypatch,
                                          run_start_args,
                                          mocked_setup_logging):
    from bigchaindb import config
    from bigchaindb.commands.bigchaindb import run_start
    from bigchaindb.common.exceptions import DatabaseAlreadyExists
    mocked_start = mocker.patch('bigchaindb.processes.start')

    def mock_run_init():
        raise DatabaseAlreadyExists()
    monkeypatch.setattr('builtins.input', lambda: '\x03')
    monkeypatch.setattr(
        'bigchaindb.commands.bigchaindb._run_init', mock_run_init)
    run_start(run_start_args)
    mocked_setup_logging.assert_called_once_with(user_log_config=config['log'])
    assert mocked_start.called


@pytest.mark.tendermint
@patch('argparse.ArgumentParser.parse_args')
@patch('bigchaindb.commands.utils.base_parser')
@patch('bigchaindb.commands.utils.start')
def test_calling_main(start_mock, base_parser_mock, parse_args_mock,
                      monkeypatch):
    from bigchaindb.commands.bigchaindb import main

    argparser_mock = Mock()
    parser = Mock()
    subparsers = Mock()
    subsubparsers = Mock()
    subparsers.add_parser.return_value = subsubparsers
    parser.add_subparsers.return_value = subparsers
    argparser_mock.return_value = parser
    monkeypatch.setattr('argparse.ArgumentParser', argparser_mock)
    main()

    assert argparser_mock.called is True
    parser.add_subparsers.assert_called_with(title='Commands',
                                             dest='command')
    subparsers.add_parser.assert_any_call('configure',
                                          help='Prepare the config file.')
    subparsers.add_parser.assert_any_call('show-config',
                                          help='Show the current '
                                          'configuration')
    subparsers.add_parser.assert_any_call('init', help='Init the database')
    subparsers.add_parser.assert_any_call('drop', help='Drop the database')

    subparsers.add_parser.assert_any_call('start', help='Start BigchainDB')

    assert start_mock.called is True


@pytest.mark.tendermint
@pytest.mark.bdb
def test_recover_db_from_zombie_txn(b, monkeypatch):
    from bigchaindb.commands.bigchaindb import run_recover
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.tendermint.lib import Block
    from bigchaindb import backend

    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset={'cycle': 'hero'},
                            metadata={'name': 'hohenheim'}) \
        .sign([alice.private_key])
    b.store_bulk_transactions([tx])
    block = Block(app_hash='random_app_hash', height=10,
                  transactions=[])._asdict()
    b.store_block(block)

    def mock_get(uri):
        return MockResponse(10)
    monkeypatch.setattr('requests.get', mock_get)

    run_recover(b)

    assert list(backend.query.get_metadata(b.connection, [tx.id])) == []
    assert not backend.query.get_asset(b.connection, tx.id)
    assert not b.get_transaction(tx.id)


@pytest.mark.tendermint
@pytest.mark.bdb
def test_recover_db_from_zombie_block(b, monkeypatch):
    from bigchaindb.commands.bigchaindb import run_recover
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.tendermint.lib import Block
    from bigchaindb import backend

    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset={'cycle': 'hero'},
                            metadata={'name': 'hohenheim'}) \
        .sign([alice.private_key])
    b.store_bulk_transactions([tx])

    block9 = Block(app_hash='random_app_hash', height=9,
                   transactions=[])._asdict()
    b.store_block(block9)
    block10 = Block(app_hash='random_app_hash', height=10,
                    transactions=[tx.id])._asdict()
    b.store_block(block10)

    def mock_get(uri):
        return MockResponse(9)
    monkeypatch.setattr('requests.get', mock_get)

    run_recover(b)

    assert list(backend.query.get_metadata(b.connection, [tx.id])) == []
    assert not backend.query.get_asset(b.connection, tx.id)
    assert not b.get_transaction(tx.id)

    block = b.get_latest_block()
    assert block['height'] == 9


@patch('bigchaindb.config_utils.autoconfigure')
@patch('bigchaindb.commands.bigchaindb.run_recover')
@patch('bigchaindb.tendermint.commands.start')
def test_recover_db_on_start(mock_autoconfigure,
                             mock_run_recover,
                             mock_start,
                             mocked_setup_logging):
    from bigchaindb.commands.bigchaindb import run_start
    args = Namespace(start_rethinkdb=False, allow_temp_keypair=False, config=None, yes=True,
                     skip_initialize_database=False)
    run_start(args)

    assert mock_run_recover.called
    assert mock_start.called


# Helper
class MockResponse():

    def __init__(self, height):
        self.height = height

    def json(self):
        return {'result': {'latest_block_height': self.height}}
