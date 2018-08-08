"""Implementation of the `bigchaindb` command,
the command-line interface (CLI) for BigchainDB Server.
"""

import os
import logging
import argparse
import copy
import json
import sys

from bigchaindb.common.exceptions import (DatabaseAlreadyExists,
                                          DatabaseDoesNotExist,
                                          MultipleValidatorOperationError)
import bigchaindb
from bigchaindb import backend
from bigchaindb.backend import schema
from bigchaindb.backend import query
from bigchaindb.backend.query import VALIDATOR_UPDATE_ID, PRE_COMMIT_ID
from bigchaindb.commands import utils
from bigchaindb.commands.utils import (configure_bigchaindb,
                                       input_on_stderr)
from bigchaindb.log import setup_logging
from bigchaindb.tendermint_utils import public_key_from_base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Note about printing:
#   We try to print to stdout for results of a command that may be useful to
#   someone (or another program). Strictly informational text, or errors,
#   should be printed to stderr.


@configure_bigchaindb
def run_show_config(args):
    """Show the current configuration"""
    # TODO Proposal: remove the "hidden" configuration. Only show config. If
    # the system needs to be configured, then display information on how to
    # configure the system.
    config = copy.deepcopy(bigchaindb.config)
    del config['CONFIGURED']
    print(json.dumps(config, indent=4, sort_keys=True))


@configure_bigchaindb
def run_configure(args):
    """Run a script to configure the current node."""
    config_path = args.config or bigchaindb.config_utils.CONFIG_DEFAULT_PATH

    config_file_exists = False
    # if the config path is `-` then it's stdout
    if config_path != '-':
        config_file_exists = os.path.exists(config_path)

    if config_file_exists and not args.yes:
        want = input_on_stderr('Config file `{}` exists, do you want to '
                               'override it? (cannot be undone) [y/N]: '.format(config_path))
        if want != 'y':
            return

    conf = copy.deepcopy(bigchaindb.config)

    # select the correct config defaults based on the backend
    print('Generating default configuration for backend {}'
          .format(args.backend), file=sys.stderr)
    database_keys = bigchaindb._database_keys_map[args.backend]
    conf['database'] = bigchaindb._database_map[args.backend]

    if not args.yes:
        for key in ('bind', ):
            val = conf['server'][key]
            conf['server'][key] = input_on_stderr('API Server {}? (default `{}`): '.format(key, val), val)

        for key in ('scheme', 'host', 'port'):
            val = conf['wsserver'][key]
            conf['wsserver'][key] = input_on_stderr('WebSocket Server {}? (default `{}`): '.format(key, val), val)

        for key in database_keys:
            val = conf['database'][key]
            conf['database'][key] = input_on_stderr('Database {}? (default `{}`): '.format(key, val), val)

        for key in ('host', 'port'):
            val = conf['tendermint'][key]
            conf['tendermint'][key] = input_on_stderr('Tendermint {}? (default `{}`)'.format(key, val), val)

    if config_path != '-':
        bigchaindb.config_utils.write_config(conf, config_path)
    else:
        print(json.dumps(conf, indent=4, sort_keys=True))
    print('Configuration written to {}'.format(config_path), file=sys.stderr)
    print('Ready to go!', file=sys.stderr)


@configure_bigchaindb
def run_upsert_validator(args):
    """Store validators which should be synced with Tendermint"""

    b = bigchaindb.BigchainDB()
    public_key = public_key_from_base64(args.public_key)
    validator = {'pub_key': {'type': 'ed25519',
                             'data': public_key},
                 'power': args.power}
    validator_update = {'validator': validator,
                        'update_id': VALIDATOR_UPDATE_ID}
    try:
        query.store_validator_update(b.connection, validator_update)
    except MultipleValidatorOperationError:
        logger.error('A validator update is pending to be applied. '
                     'Please re-try after the current update has '
                     'been processed.')


def _run_init():
    bdb = bigchaindb.BigchainDB()

    schema.init_database(connection=bdb.connection)


@configure_bigchaindb
def run_init(args):
    """Initialize the database"""
    # TODO Provide mechanism to:
    # 1. prompt the user to inquire whether they wish to drop the db
    # 2. force the init, (e.g., via -f flag)
    try:
        _run_init()
    except DatabaseAlreadyExists:
        print('The database already exists.', file=sys.stderr)
        print('If you wish to re-initialize it, first drop it.', file=sys.stderr)


@configure_bigchaindb
def run_drop(args):
    """Drop the database"""
    dbname = bigchaindb.config['database']['name']

    if not args.yes:
        response = input_on_stderr('Do you want to drop `{}` database? [y/n]: '.format(dbname))
        if response != 'y':
            return

    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']
    try:
        schema.drop_database(conn, dbname)
    except DatabaseDoesNotExist:
        print("Cannot drop '{name}'. The database does not exist.".format(name=dbname), file=sys.stderr)


def run_recover(b):
    pre_commit = query.get_pre_commit_state(b.connection, PRE_COMMIT_ID)

    # Initially the pre-commit collection would be empty
    if pre_commit:
        latest_block = query.get_latest_block(b.connection)

        # NOTE: the pre-commit state can only be ahead of the commited state
        # by 1 block
        if latest_block and (latest_block['height'] < pre_commit['height']):
            query.delete_transactions(b.connection, pre_commit['transactions'])


@configure_bigchaindb
def run_start(args):
    """Start the processes to run the node"""

    # Configure Logging
    setup_logging()

    logger.info('BigchainDB Version %s', bigchaindb.__version__)
    run_recover(bigchaindb.lib.BigchainDB())

    try:
        if not args.skip_initialize_database:
            logger.info('Initializing database')
            _run_init()
    except DatabaseAlreadyExists:
        pass

    logger.info('Starting BigchainDB main process.')
    from bigchaindb.start import start
    start()


def create_parser():
    parser = argparse.ArgumentParser(
        description='Control your BigchainDB node.',
        parents=[utils.base_parser])

    # all the commands are contained in the subparsers object,
    # the command selected by the user will be stored in `args.command`
    # that is used by the `main` function to select which other
    # function to call.
    subparsers = parser.add_subparsers(title='Commands',
                                       dest='command')

    # parser for writing a config file
    config_parser = subparsers.add_parser('configure',
                                          help='Prepare the config file.')

    config_parser.add_argument('backend',
                               choices=['localmongodb'],
                               default='localmongodb',
                               const='localmongodb',
                               nargs='?',
                               help='The backend to use. It can only be '
                               '"localmongodb", currently.')

    validator_parser = subparsers.add_parser('upsert-validator',
                                             help='Add/update/delete a validator')

    validator_parser.add_argument('public_key',
                                  help='Public key of the validator.')

    validator_parser.add_argument('power',
                                  type=int,
                                  help='Voting power of the validator. '
                                  'Setting it to 0 will delete the validator.')

    # parsers for showing/exporting config values
    subparsers.add_parser('show-config',
                          help='Show the current configuration')

    # parser for database-level commands
    subparsers.add_parser('init',
                          help='Init the database')

    subparsers.add_parser('drop',
                          help='Drop the database')

    # parser for starting BigchainDB
    start_parser = subparsers.add_parser('start',
                                         help='Start BigchainDB')

    start_parser.add_argument('--no-init',
                              dest='skip_initialize_database',
                              default=False,
                              action='store_true',
                              help='Skip database initialization')

    return parser


def main():
    utils.start(create_parser(), sys.argv[1:], globals())
