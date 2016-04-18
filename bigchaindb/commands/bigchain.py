"""Implementation of the `bigchaindb` command,
which is one of the commands in the BigchainDB
command-line interface.
"""

import os
import sys
import logging
import argparse
import copy
import json

import bigchaindb
import bigchaindb.config_utils
from bigchaindb import db
from bigchaindb.exceptions import DatabaseAlreadyExists, KeypairNotFoundException
from bigchaindb.commands.utils import base_parser, start
from bigchaindb.processes import Processes
from bigchaindb import crypto


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_show_config(args):
    """Show the current configuration"""
    # TODO Proposal: remove the "hidden" configuration. Only show config. If
    # the system needs to be configured, then display information on how to
    # configure the system.
    bigchaindb.config_utils.autoconfigure(filename=args.config, force=True)
    config = copy.deepcopy(bigchaindb.config)
    del config['CONFIGURED']
    private_key = config['keypair']['private']
    config['keypair']['private'] = 'x' * 45 if private_key else None
    print(json.dumps(config, indent=4, sort_keys=True))


def run_configure(args, skip_if_exists=False):
    """Run a script to configure the current node.

    Args:
        skip_if_exists (bool): skip the function if a config file already exists
    """
    config_path = args.config or bigchaindb.config_utils.CONFIG_DEFAULT_PATH
    config_file_exists = os.path.exists(config_path)

    if config_file_exists and skip_if_exists:
        return

    if config_file_exists and not args.yes:
        want = input('Config file `{}` exists, do you want to override it? '
                     '(cannot be undone) [y/N]: '.format(config_path))
        if want != 'y':
            return

    # Patch the default configuration with the new values
    conf = copy.deepcopy(bigchaindb._config)

    print('Generating keypair')
    conf['keypair']['private'], conf['keypair']['public'] = \
        crypto.generate_key_pair()

    if not args.yes:
        for key in ('bind', ):
            val = conf['server'][key]
            conf['server'][key] = \
                input('API Server {}? (default `{}`): '.format(key, val)) \
                or val

        for key in ('host', 'port', 'name'):
            val = conf['database'][key]
            conf['database'][key] = \
                input('Database {}? (default `{}`): '.format(key, val)) \
                or val

        for key in ('host', 'port', 'rate'):
            val = conf['statsd'][key]
            conf['statsd'][key] = \
                input('Statsd {}? (default `{}`): '.format(key, val)) \
                or val

    bigchaindb.config_utils.write_config(conf, config_path)
    print('Configuration written to {}'.format(config_path))
    print('Ready to go!')


def run_export_my_pubkey(args):
    """Export this node's public key to standard output
    """
    logger.debug('bigchaindb args = {}'.format(args))
    bigchaindb.config_utils.autoconfigure(filename=args.config, force=True)
    pubkey = bigchaindb.config['keypair']['public']
    if pubkey is not None:
        print(pubkey)
    else:
        sys.exit("This node's public key wasn't set anywhere "
                 "so it can't be exported")
        # raises SystemExit exception
        # message is sent to stderr
        # exits with exit code 1 (signals tha an error happened)


def run_init(args):
    """Initialize the database"""
    bigchaindb.config_utils.autoconfigure(filename=args.config, force=True)
    # TODO Provide mechanism to:
    # 1. prompt the user to inquire whether they wish to drop the db
    # 2. force the init, (e.g., via -f flag)
    try:
        db.init()
    except DatabaseAlreadyExists:
        print('The database already exists.')
        print('If you wish to re-initialize it, first drop it.')


def run_drop(args):
    """Drop the database"""
    bigchaindb.config_utils.autoconfigure(filename=args.config, force=True)
    db.drop(assume_yes=args.yes)


def run_start(args):
    """Start the processes to run the node"""
    # run_configure(args, skip_if_exists=True)
    bigchaindb.config_utils.autoconfigure(filename=args.config, force=True)
    try:
        db.init()
    except DatabaseAlreadyExists:
        pass
    except KeypairNotFoundException:
        sys.exit("Can't start BigchainDB, no keypair found. "
                 'Did you run `bigchaindb configure`?')

    processes = Processes()
    logger.info('Starting BigchainDB main process')
    processes.start()


def main():
    parser = argparse.ArgumentParser(
        description='Control your BigchainDB node.',
        parents=[base_parser])

    # all the commands are contained in the subparsers object,
    # the command selected by the user will be stored in `args.command`
    # that is used by the `main` function to select which other
    # function to call.
    subparsers = parser.add_subparsers(title='Commands',
                                       dest='command')

    # parser for writing a config file
    subparsers.add_parser('configure',
                          help='Prepare the config file '
                               'and create the node keypair')

    # parsers for showing/exporting config values
    subparsers.add_parser('show-config',
                          help='Show the current configuration')

    subparsers.add_parser('export-my-pubkey',
                          help="Export this node's public key")

    # parser for database-level commands
    subparsers.add_parser('init',
                          help='Init the database')

    subparsers.add_parser('drop',
                          help='Drop the database')

    # parser for starting BigchainDB
    subparsers.add_parser('start',
                          help='Start BigchainDB')

    start(parser, globals())


if __name__ == '__main__':
    main()
