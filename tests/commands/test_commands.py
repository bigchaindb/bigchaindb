import json
from unittest.mock import Mock, patch
from argparse import Namespace, ArgumentTypeError
import copy

import pytest


def test_make_sure_we_dont_remove_any_command():
    # thanks to: http://stackoverflow.com/a/18161115/597097
    from bigchaindb.commands.bigchain import create_parser

    parser = create_parser()

    assert parser.parse_args(['configure', 'rethinkdb']).command
    assert parser.parse_args(['configure', 'mongodb']).command
    assert parser.parse_args(['show-config']).command
    assert parser.parse_args(['export-my-pubkey']).command
    assert parser.parse_args(['init']).command
    assert parser.parse_args(['drop']).command
    assert parser.parse_args(['start']).command
    assert parser.parse_args(['set-shards', '1']).command
    assert parser.parse_args(['set-replicas', '1']).command
    assert parser.parse_args(['load']).command
    assert parser.parse_args(['add-replicas', 'localhost:27017']).command
    assert parser.parse_args(['remove-replicas', 'localhost:27017']).command


def test_start_raises_if_command_not_implemented():
    from bigchaindb.commands.bigchain import utils
    from bigchaindb.commands.bigchain import create_parser

    parser = create_parser()

    with pytest.raises(NotImplementedError):
        # Will raise because `scope`, the third parameter,
        # doesn't contain the function `run_start`
        utils.start(parser, ['start'], {})


def test_start_raises_if_no_arguments_given():
    from bigchaindb.commands.bigchain import utils
    from bigchaindb.commands.bigchain import create_parser

    parser = create_parser()

    with pytest.raises(SystemExit):
        utils.start(parser, [], {})


@patch('multiprocessing.cpu_count', return_value=42)
def test_start_sets_multiprocess_var_based_on_cli_args(mock_cpu_count):
    from bigchaindb.commands.bigchain import utils
    from bigchaindb.commands.bigchain import create_parser

    def run_load(args):
        return args

    parser = create_parser()

    assert utils.start(parser, ['load'], {'run_load': run_load}).multiprocess == 1
    assert utils.start(parser, ['load', '--multiprocess'], {'run_load': run_load}).multiprocess == 42


@patch('bigchaindb.commands.utils.start')
def test_main_entrypoint(mock_start):
    from bigchaindb.commands.bigchain import main
    main()

    assert mock_start.called


def test_bigchain_run_start(mock_run_configure, mock_processes_start, mock_db_init_with_existing_db):
    from bigchaindb.commands.bigchain import run_start
    args = Namespace(start_rethinkdb=False, allow_temp_keypair=False, config=None, yes=True)
    run_start(args)


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
@pytest.mark.usefixtures('ignore_local_config_file')
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


@patch('bigchaindb.backend.schema.drop_database')
def test_drop_db_when_assumed_yes(mock_db_drop):
    from bigchaindb.commands.bigchain import run_drop
    args = Namespace(config=None, yes=True)

    run_drop(args)
    assert mock_db_drop.called


@patch('bigchaindb.backend.schema.drop_database')
def test_drop_db_when_interactive_yes(mock_db_drop, monkeypatch):
    from bigchaindb.commands.bigchain import run_drop
    args = Namespace(config=None, yes=False)
    monkeypatch.setattr('bigchaindb.commands.bigchain.input_on_stderr', lambda x: 'y')

    run_drop(args)
    assert mock_db_drop.called


@patch('bigchaindb.backend.schema.drop_database')
def test_drop_db_does_not_drop_when_interactive_no(mock_db_drop, monkeypatch):
    from bigchaindb.commands.bigchain import run_drop
    args = Namespace(config=None, yes=False)
    monkeypatch.setattr('bigchaindb.commands.bigchain.input_on_stderr', lambda x: 'n')

    run_drop(args)
    assert not mock_db_drop.called


def test_run_configure_when_config_exists_and_skipping(monkeypatch):
    from bigchaindb.commands.bigchain import run_configure
    monkeypatch.setattr('os.path.exists', lambda path: True)
    args = Namespace(config='foo', yes=True)
    return_value = run_configure(args, skip_if_exists=True)
    assert return_value is None


# TODO Beware if you are putting breakpoints in there, and using the '-s'
# switch with pytest. It will just hang. Seems related to the monkeypatching of
# input_on_stderr.
def test_run_configure_when_config_does_not_exist(monkeypatch,
                                                  mock_write_config,
                                                  mock_generate_key_pair,
                                                  mock_bigchaindb_backup_config):
    from bigchaindb.commands.bigchain import run_configure
    monkeypatch.setattr('os.path.exists', lambda path: False)
    monkeypatch.setattr('builtins.input', lambda: '\n')
    args = Namespace(config='foo', backend='rethinkdb', yes=True)
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


@pytest.mark.parametrize('backend', (
    'rethinkdb',
    'mongodb',
))
def test_run_configure_with_backend(backend, monkeypatch, mock_write_config):
    import bigchaindb
    from bigchaindb.commands.bigchain import run_configure

    value = {}

    def mock_write_config(new_config, filename=None):
        value['return'] = new_config

    monkeypatch.setattr('os.path.exists', lambda path: False)
    monkeypatch.setattr('builtins.input', lambda: '\n')
    monkeypatch.setattr('bigchaindb.config_utils.write_config',
                        mock_write_config)

    args = Namespace(config='foo', backend=backend, yes=True)
    expected_config = bigchaindb.config
    run_configure(args)

    # update the expected config with the correct backend and keypair
    backend_conf = getattr(bigchaindb, '_database_' + backend)
    expected_config.update({'database': backend_conf,
                            'keypair': value['return']['keypair']})

    assert value['return'] == expected_config


@patch('bigchaindb.common.crypto.generate_key_pair',
       return_value=('private_key', 'public_key'))
@pytest.mark.usefixtures('ignore_local_config_file')
def test_allow_temp_keypair_generates_one_on_the_fly(mock_gen_keypair,
                                                     mock_processes_start,
                                                     mock_db_init_with_existing_db):
    import bigchaindb
    from bigchaindb.commands.bigchain import run_start

    bigchaindb.config['keypair'] = {'private': None, 'public': None}

    args = Namespace(allow_temp_keypair=True, start_rethinkdb=False, config=None, yes=True)
    run_start(args)

    assert bigchaindb.config['keypair']['private'] == 'private_key'
    assert bigchaindb.config['keypair']['public'] == 'public_key'


@patch('bigchaindb.common.crypto.generate_key_pair',
       return_value=('private_key', 'public_key'))
@pytest.mark.usefixtures('ignore_local_config_file')
def test_allow_temp_keypair_doesnt_override_if_keypair_found(mock_gen_keypair,
                                                             mock_processes_start,
                                                             mock_db_init_with_existing_db):
    import bigchaindb
    from bigchaindb.commands.bigchain import run_start

    # Preconditions for the test
    original_private_key = bigchaindb.config['keypair']['private']
    original_public_key = bigchaindb.config['keypair']['public']

    assert isinstance(original_public_key, str)
    assert isinstance(original_private_key, str)

    args = Namespace(allow_temp_keypair=True, start_rethinkdb=False, config=None, yes=True)
    run_start(args)

    assert bigchaindb.config['keypair']['private'] == original_private_key
    assert bigchaindb.config['keypair']['public'] == original_public_key


@patch('argparse.ArgumentParser.parse_args')
@patch('bigchaindb.commands.utils.base_parser')
@patch('bigchaindb.commands.utils.start')
def test_calling_main(start_mock, base_parser_mock, parse_args_mock,
                      monkeypatch):
    from bigchaindb.commands.bigchain import main

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
    assert parser.add_argument.called is True
    parser.add_argument.assert_any_call('--dev-start-rethinkdb',
                                        dest='start_rethinkdb',
                                        action='store_true',
                                        help='Run RethinkDB on start')
    parser.add_subparsers.assert_called_with(title='Commands',
                                             dest='command')
    subparsers.add_parser.assert_any_call('configure',
                                          help='Prepare the config file '
                                          'and create the node keypair')
    subparsers.add_parser.assert_any_call('show-config',
                                          help='Show the current '
                                          'configuration')
    subparsers.add_parserassert_any_call('export-my-pubkey',
                                         help="Export this node's public "
                                         'key')
    subparsers.add_parser.assert_any_call('init', help='Init the database')
    subparsers.add_parser.assert_any_call('drop', help='Drop the database')
    subparsers.add_parser.assert_any_call('start', help='Start BigchainDB')

    subparsers.add_parser.assert_any_call('set-shards',
                                          help='Configure number of shards')

    subsubparsers.add_argument.assert_any_call('num_shards',
                                               metavar='num_shards',
                                               type=int, default=1,
                                               help='Number of shards')

    subparsers.add_parser.assert_any_call('set-replicas',
                                          help='Configure number of replicas')
    subsubparsers.add_argument.assert_any_call('num_replicas',
                                               metavar='num_replicas',
                                               type=int, default=1,
                                               help='Number of replicas (i.e. '
                                               'the replication factor)')

    subparsers.add_parser.assert_any_call('load',
                                          help='Write transactions to the '
                                          'backlog')

    subsubparsers.add_argument.assert_any_call('-m', '--multiprocess',
                                               nargs='?', type=int,
                                               default=False,
                                               help='Spawn multiple processes '
                                               'to run the command, if no '
                                               'value is provided, the number '
                                               'of processes is equal to the '
                                               'number of cores of the host '
                                               'machine')
    subsubparsers.add_argument.assert_any_call('-c', '--count',
                                               default=0,
                                               type=int,
                                               help='Number of transactions '
                                               'to push. If the parameter -m '
                                               'is set, the count is '
                                               'distributed equally to all '
                                               'the processes')
    assert start_mock.called is True


@pytest.mark.usefixtures('ignore_local_config_file')
@patch('bigchaindb.commands.bigchain.add_replicas')
def test_run_add_replicas(mock_add_replicas):
    from bigchaindb.commands.bigchain import run_add_replicas
    from bigchaindb.backend.exceptions import DatabaseOpFailedError

    args = Namespace(config=None, replicas=['localhost:27017'])

    # test add_replicas no raises
    mock_add_replicas.return_value = None
    assert run_add_replicas(args) is None
    assert mock_add_replicas.call_count == 1
    mock_add_replicas.reset_mock()

    # test add_replicas with `DatabaseOpFailedError`
    mock_add_replicas.side_effect = DatabaseOpFailedError()
    assert run_add_replicas(args) is None
    assert mock_add_replicas.call_count == 1
    mock_add_replicas.reset_mock()

    # test add_replicas with `NotImplementedError`
    mock_add_replicas.side_effect = NotImplementedError()
    assert run_add_replicas(args) is None
    assert mock_add_replicas.call_count == 1
    mock_add_replicas.reset_mock()


@pytest.mark.usefixtures('ignore_local_config_file')
@patch('bigchaindb.commands.bigchain.remove_replicas')
def test_run_remove_replicas(mock_remove_replicas):
    from bigchaindb.commands.bigchain import run_remove_replicas
    from bigchaindb.backend.exceptions import DatabaseOpFailedError

    args = Namespace(config=None, replicas=['localhost:27017'])

    # test add_replicas no raises
    mock_remove_replicas.return_value = None
    assert run_remove_replicas(args) is None
    assert mock_remove_replicas.call_count == 1
    mock_remove_replicas.reset_mock()

    # test add_replicas with `DatabaseOpFailedError`
    mock_remove_replicas.side_effect = DatabaseOpFailedError()
    assert run_remove_replicas(args) is None
    assert mock_remove_replicas.call_count == 1
    mock_remove_replicas.reset_mock()

    # test add_replicas with `NotImplementedError`
    mock_remove_replicas.side_effect = NotImplementedError()
    assert run_remove_replicas(args) is None
    assert mock_remove_replicas.call_count == 1
    mock_remove_replicas.reset_mock()


def test_mongodb_host_type():
    from bigchaindb.commands.utils import mongodb_host

    # bad port provided
    with pytest.raises(ArgumentTypeError):
        mongodb_host('localhost:11111111111')

    # no port information provided
    with pytest.raises(ArgumentTypeError):
        mongodb_host('localhost')

    # bad host provided
    with pytest.raises(ArgumentTypeError):
        mongodb_host(':27017')
