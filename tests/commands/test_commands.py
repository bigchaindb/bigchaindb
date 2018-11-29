# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import json
import logging

from unittest.mock import Mock, patch
from argparse import Namespace

import pytest

from bigchaindb import ValidatorElection
from bigchaindb.commands.bigchaindb import run_election_show
from bigchaindb.elections.election import Election
from bigchaindb.lib import Block
from bigchaindb.migrations.chain_migration_election import ChainMigrationElection

from tests.utils import generate_election, generate_validators


def test_make_sure_we_dont_remove_any_command():
    # thanks to: http://stackoverflow.com/a/18161115/597097
    from bigchaindb.commands.bigchaindb import create_parser

    parser = create_parser()

    assert parser.parse_args(['configure', 'localmongodb']).command
    assert parser.parse_args(['show-config']).command
    assert parser.parse_args(['init']).command
    assert parser.parse_args(['drop']).command
    assert parser.parse_args(['start']).command
    assert parser.parse_args(['election', 'new', 'upsert-validator', 'TEMP_PUB_KEYPAIR', '10', 'TEMP_NODE_ID',
                              '--private-key', 'TEMP_PATH_TO_PRIVATE_KEY']).command
    assert parser.parse_args(['election', 'new', 'chain-migration',
                              '--private-key', 'TEMP_PATH_TO_PRIVATE_KEY']).command
    assert parser.parse_args(['election', 'approve', 'ELECTION_ID', '--private-key',
                              'TEMP_PATH_TO_PRIVATE_KEY']).command
    assert parser.parse_args(['election', 'show', 'ELECTION_ID']).command
    assert parser.parse_args(['tendermint-version']).command


@patch('bigchaindb.commands.utils.start')
def test_main_entrypoint(mock_start):
    from bigchaindb.commands.bigchaindb import main
    main()

    assert mock_start.called


@patch('bigchaindb.log.setup_logging')
@patch('bigchaindb.commands.bigchaindb._run_init')
@patch('bigchaindb.config_utils.autoconfigure')
def test_bigchain_run_start(mock_setup_logging, mock_run_init,
                            mock_autoconfigure, mock_processes_start):
    from bigchaindb.commands.bigchaindb import run_start
    args = Namespace(config=None, yes=True,
                     skip_initialize_database=False)
    run_start(args)
    assert mock_setup_logging.called


# TODO Please beware, that if debugging, the "-s" switch for pytest will
# interfere with capsys.
# See related issue: https://github.com/pytest-dev/pytest/issues/128
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
    assert output_config == config


def test__run_init(mocker):
    from bigchaindb.commands.bigchaindb import _run_init
    bigchain_mock = mocker.patch(
        'bigchaindb.commands.bigchaindb.bigchaindb.BigchainDB')
    init_db_mock = mocker.patch(
        'bigchaindb.commands.bigchaindb.schema.init_database',
        autospec=True,
        spec_set=True,
    )
    _run_init()
    bigchain_mock.assert_called_once_with()
    init_db_mock.assert_called_once_with(
        connection=bigchain_mock.return_value.connection)


@patch('bigchaindb.backend.schema.drop_database')
def test_drop_db_when_assumed_yes(mock_db_drop):
    from bigchaindb.commands.bigchaindb import run_drop
    args = Namespace(config=None, yes=True)

    run_drop(args)
    assert mock_db_drop.called


@patch('bigchaindb.backend.schema.drop_database')
def test_drop_db_when_interactive_yes(mock_db_drop, monkeypatch):
    from bigchaindb.commands.bigchaindb import run_drop
    args = Namespace(config=None, yes=False)
    monkeypatch.setattr(
        'bigchaindb.commands.bigchaindb.input_on_stderr', lambda x: 'y')

    run_drop(args)
    assert mock_db_drop.called


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


def test_run_configure_when_config_does_exist(monkeypatch,
                                              mock_write_config,
                                              mock_generate_key_pair,
                                              mock_bigchaindb_backup_config):
    value = {}

    def mock_write_config(newconfig):
        value['return'] = newconfig

    from bigchaindb.commands.bigchaindb import run_configure
    monkeypatch.setattr('os.path.exists', lambda path: True)
    monkeypatch.setattr('builtins.input', lambda: '\n')
    monkeypatch.setattr(
        'bigchaindb.config_utils.write_config', mock_write_config)

    args = Namespace(config=None, yes=None)
    run_configure(args)
    assert value == {}


@pytest.mark.skip
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


@patch('bigchaindb.commands.utils.start')
def test_calling_main(start_mock, monkeypatch):
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
    subparsers.add_parser.assert_any_call('tendermint-version',
                                          help='Show the Tendermint supported '
                                          'versions')

    assert start_mock.called is True


@patch('bigchaindb.commands.bigchaindb.run_recover')
@patch('bigchaindb.start.start')
def test_recover_db_on_start(mock_run_recover,
                             mock_start,
                             mocked_setup_logging):
    from bigchaindb.commands.bigchaindb import run_start
    args = Namespace(config=None, yes=True,
                     skip_initialize_database=False)
    run_start(args)

    assert mock_run_recover.called
    assert mock_start.called


@pytest.mark.bdb
def test_run_recover(b, alice, bob):
    from bigchaindb.commands.bigchaindb import run_recover
    from bigchaindb.models import Transaction
    from bigchaindb.lib import Block
    from bigchaindb.backend import query

    tx1 = Transaction.create([alice.public_key],
                             [([alice.public_key], 1)],
                             asset={'cycle': 'hero'},
                             metadata={'name': 'hohenheim'}) \
                     .sign([alice.private_key])
    tx2 = Transaction.create([bob.public_key],
                             [([bob.public_key], 1)],
                             asset={'cycle': 'hero'},
                             metadata={'name': 'hohenheim'}) \
                     .sign([bob.private_key])

    # store the transactions
    b.store_bulk_transactions([tx1, tx2])

    # create a random block
    block8 = Block(app_hash='random_app_hash1', height=8,
                   transactions=['txid_doesnt_matter'])._asdict()
    b.store_block(block8)

    # create the next block
    block9 = Block(app_hash='random_app_hash1', height=9,
                   transactions=[tx1.id])._asdict()
    b.store_block(block9)

    # create a pre_commit state which is ahead of the commit state
    pre_commit_state = dict(height=10, transactions=[tx2.id])
    b.store_pre_commit_state(pre_commit_state)

    run_recover(b)

    assert not query.get_transaction(b.connection, tx2.id)


# Helper
class MockResponse():

    def __init__(self, height):
        self.height = height

    def json(self):
        return {'result': {'latest_block_height': self.height}}


@pytest.mark.abci
def test_election_new_upsert_validator_with_tendermint(b, priv_validator_path, user_sk, validators):
    from bigchaindb.commands.bigchaindb import run_election_new_upsert_validator

    new_args = Namespace(action='new',
                         election_type='upsert-validator',
                         public_key='HHG0IQRybpT6nJMIWWFWhMczCLHt6xcm7eP52GnGuPY=',
                         power=1,
                         node_id='unique_node_id_for_test_upsert_validator_new_with_tendermint',
                         sk=priv_validator_path,
                         config={})

    election_id = run_election_new_upsert_validator(new_args, b)

    assert b.get_transaction(election_id)


@pytest.mark.bdb
def test_election_new_upsert_validator_without_tendermint(caplog, b, priv_validator_path, user_sk):
    from bigchaindb.commands.bigchaindb import run_election_new_upsert_validator

    def mock_write(tx, mode):
        b.store_bulk_transactions([tx])
        return (202, '')

    b.get_validators = mock_get_validators
    b.write_transaction = mock_write

    args = Namespace(action='new',
                     election_type='upsert-validator',
                     public_key='CJxdItf4lz2PwEf4SmYNAu/c/VpmX39JEgC5YpH7fxg=',
                     power=1,
                     node_id='fb7140f03a4ffad899fabbbf655b97e0321add66',
                     sk=priv_validator_path,
                     config={})

    with caplog.at_level(logging.INFO):
        election_id = run_election_new_upsert_validator(args, b)
        assert caplog.records[0].msg == '[SUCCESS] Submitted proposal with id: ' + election_id
        assert b.get_transaction(election_id)


@pytest.mark.abci
def test_election_new_chain_migration_with_tendermint(b, priv_validator_path, user_sk, validators):
    from bigchaindb.commands.bigchaindb import run_election_new_chain_migration

    new_args = Namespace(action='new',
                         election_type='migration',
                         sk=priv_validator_path,
                         config={})

    election_id = run_election_new_chain_migration(new_args, b)

    assert b.get_transaction(election_id)


@pytest.mark.bdb
def test_election_new_chain_migration_without_tendermint(caplog, b, priv_validator_path, user_sk):
    from bigchaindb.commands.bigchaindb import run_election_new_chain_migration

    def mock_write(tx, mode):
        b.store_bulk_transactions([tx])
        return (202, '')

    b.get_validators = mock_get_validators
    b.write_transaction = mock_write

    args = Namespace(action='new',
                     election_type='migration',
                     sk=priv_validator_path,
                     config={})

    with caplog.at_level(logging.INFO):
        election_id = run_election_new_chain_migration(args, b)
        assert caplog.records[0].msg == '[SUCCESS] Submitted proposal with id: ' + election_id
        assert b.get_transaction(election_id)


@pytest.mark.bdb
def test_election_new_upsert_validator_invalid_election(caplog, b, priv_validator_path, user_sk):
    from bigchaindb.commands.bigchaindb import run_election_new_upsert_validator

    args = Namespace(action='new',
                     election_type='upsert-validator',
                     public_key='CJxdItf4lz2PwEf4SmYNAu/c/VpmX39JEgC5YpH7fxg=',
                     power=10,
                     node_id='fb7140f03a4ffad899fabbbf655b97e0321add66',
                     sk='/tmp/invalid/path/key.json',
                     config={})

    with caplog.at_level(logging.ERROR):
        assert not run_election_new_upsert_validator(args, b)
        assert caplog.records[0].msg.__class__ == FileNotFoundError


@pytest.mark.bdb
def test_election_new_upsert_validator_invalid_power(caplog, b, priv_validator_path, user_sk):
    from bigchaindb.commands.bigchaindb import run_election_new_upsert_validator
    from bigchaindb.common.exceptions import InvalidPowerChange

    def mock_write(tx, mode):
        b.store_bulk_transactions([tx])
        return (400, '')

    b.write_transaction = mock_write
    b.get_validators = mock_get_validators
    args = Namespace(action='new',
                     election_type='upsert-validator',
                     public_key='CJxdItf4lz2PwEf4SmYNAu/c/VpmX39JEgC5YpH7fxg=',
                     power=10,
                     node_id='fb7140f03a4ffad899fabbbf655b97e0321add66',
                     sk=priv_validator_path,
                     config={})

    with caplog.at_level(logging.ERROR):
        assert not run_election_new_upsert_validator(args, b)
        assert caplog.records[0].msg.__class__ == InvalidPowerChange


@pytest.mark.abci
def test_election_approve_with_tendermint(b, priv_validator_path, user_sk, validators):
    from bigchaindb.commands.bigchaindb import (run_election_new_upsert_validator,
                                                run_election_approve)

    public_key = 'CJxdItf4lz2PwEf4SmYNAu/c/VpmX39JEgC5YpH7fxg='
    new_args = Namespace(action='new',
                         election_type='upsert-validator',
                         public_key=public_key,
                         power=1,
                         node_id='fb7140f03a4ffad899fabbbf655b97e0321add66',
                         sk=priv_validator_path,
                         config={})

    election_id = run_election_new_upsert_validator(new_args, b)
    assert election_id

    args = Namespace(action='approve',
                     election_id=election_id,
                     sk=priv_validator_path,
                     config={})
    approve = run_election_approve(args, b)

    assert b.get_transaction(approve)


@pytest.mark.bdb
def test_election_approve_without_tendermint(caplog, b, priv_validator_path, new_validator, node_key):
    from bigchaindb.commands.bigchaindb import run_election_approve
    from argparse import Namespace

    b, election_id = call_election(b, new_validator, node_key)

    # call run_election_approve with args that point to the election
    args = Namespace(action='approve',
                     election_id=election_id,
                     sk=priv_validator_path,
                     config={})

    # assert returned id is in the db
    with caplog.at_level(logging.INFO):
        approval_id = run_election_approve(args, b)
        assert caplog.records[0].msg == '[SUCCESS] Your vote has been submitted'
        assert b.get_transaction(approval_id)


@pytest.mark.bdb
def test_election_approve_failure(caplog, b, priv_validator_path, new_validator, node_key):
    from bigchaindb.commands.bigchaindb import run_election_approve
    from argparse import Namespace

    b, election_id = call_election(b, new_validator, node_key)

    def mock_write(tx, mode):
        b.store_bulk_transactions([tx])
        return (400, '')

    b.write_transaction = mock_write

    # call run_upsert_validator_approve with args that point to the election
    args = Namespace(action='approve',
                     election_id=election_id,
                     sk=priv_validator_path,
                     config={})

    with caplog.at_level(logging.ERROR):
        assert not run_election_approve(args, b)
        assert caplog.records[0].msg == 'Failed to commit vote'


@pytest.mark.bdb
def test_election_approve_called_with_bad_key(caplog, b, bad_validator_path, new_validator, node_key):
    from bigchaindb.commands.bigchaindb import run_election_approve
    from argparse import Namespace

    b, election_id = call_election(b, new_validator, node_key)

    # call run_upsert_validator_approve with args that point to the election, but a bad signing key
    args = Namespace(action='approve',
                     election_id=election_id,
                     sk=bad_validator_path,
                     config={})

    with caplog.at_level(logging.ERROR):
        assert not run_election_approve(args, b)
        assert caplog.records[0].msg == 'The key you provided does not match any of '\
            'the eligible voters in this election.'


@pytest.mark.bdb
def test_chain_migration_election_show_shows_inconclusive(b):
    validators = generate_validators([1] * 4)
    b.store_validator_set(1, [v['storage'] for v in validators])

    public_key = validators[0]['public_key']
    private_key = validators[0]['private_key']
    voter_keys = [v['private_key'] for v in validators]

    election, votes = generate_election(b,
                                        ChainMigrationElection,
                                        public_key, private_key,
                                        {},
                                        voter_keys)

    assert not run_election_show(Namespace(election_id=election.id), b)

    Election.process_block(b, 1, [election])
    b.store_bulk_transactions([election])

    assert run_election_show(Namespace(election_id=election.id), b) == \
        'status=ongoing'

    b.store_block(Block(height=1, transactions=[], app_hash='')._asdict())
    b.store_validator_set(2, [v['storage'] for v in validators])

    assert run_election_show(Namespace(election_id=election.id), b) == \
        'status=ongoing'

    b.store_block(Block(height=2, transactions=[], app_hash='')._asdict())
    # TODO insert yet another block here when upgrading to Tendermint 0.22.4.

    assert run_election_show(Namespace(election_id=election.id), b) == \
        'status=inconclusive'


@pytest.mark.bdb
def test_chain_migration_election_show_shows_concluded(b):
    validators = generate_validators([1] * 4)
    b.store_validator_set(1, [v['storage'] for v in validators])

    public_key = validators[0]['public_key']
    private_key = validators[0]['private_key']
    voter_keys = [v['private_key'] for v in validators]

    election, votes = generate_election(b,
                                        ChainMigrationElection,
                                        public_key, private_key,
                                        {},
                                        voter_keys)

    assert not run_election_show(Namespace(election_id=election.id), b)

    b.store_bulk_transactions([election])
    Election.process_block(b, 1, [election])

    assert run_election_show(Namespace(election_id=election.id), b) == \
        'status=ongoing'

    b.store_abci_chain(1, 'chain-X')
    b.store_block(Block(height=1,
                        transactions=[v.id for v in votes],
                        app_hash='last_app_hash')._asdict())
    Election.process_block(b, 2, votes)

    assert run_election_show(Namespace(election_id=election.id), b) == \
        f'''status=concluded
chain_id=chain-X-migrated-at-height-1
app_hash=last_app_hash
validators=[{''.join([f"""
    {{
        "pub_key": {{
            "type": "tendermint/PubKeyEd25519",
            "value": "{v['public_key']}"
        }},
        "power": {v['storage']['voting_power']}
    }}{',' if i + 1 != len(validators) else ''}""" for i, v in enumerate(validators)])}
]'''


def test_bigchain_tendermint_version(capsys):
    from bigchaindb.commands.bigchaindb import run_tendermint_version

    args = Namespace(config=None)
    _, _ = capsys.readouterr()
    run_tendermint_version(args)
    output_config = json.loads(capsys.readouterr()[0])
    from bigchaindb.version import __tm_supported_versions__
    assert len(output_config["tendermint"]) == len(__tm_supported_versions__)
    assert sorted(output_config["tendermint"]) == sorted(__tm_supported_versions__)


def mock_get_validators(height):
    return [
        {'public_key': {'value': "zL/DasvKulXZzhSNFwx4cLRXKkSM9GPK7Y0nZ4FEylM=",
                        'type': 'ed25519-base64'},
         'voting_power': 10}
    ]


def call_election(b, new_validator, node_key):

    def mock_write(tx, mode):
        b.store_bulk_transactions([tx])
        return (202, '')

    # patch the validator set. We now have one validator with power 10
    b.get_validators = mock_get_validators
    b.write_transaction = mock_write

    # our voters is a list of length 1, populated from our mocked validator
    voters = ValidatorElection.recipients(b)
    # and our voter is the public key from the voter list
    voter = node_key.public_key
    valid_election = ValidatorElection.generate([voter],
                                                voters,
                                                new_validator, None).sign([node_key.private_key])

    # patch in an election with a vote issued to the user
    election_id = valid_election.id
    b.store_bulk_transactions([valid_election])

    return b, election_id
