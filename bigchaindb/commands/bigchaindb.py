"""Implementation of the `bigchaindb` command,
the command-line interface (CLI) for BigchainDB Server.
"""

import os
import logging
import argparse
import copy
import json
import sys

from bigchaindb.common import crypto
from bigchaindb.common.exceptions import (StartupError,
                                          DatabaseAlreadyExists,
                                          KeypairNotFoundException,
                                          DatabaseDoesNotExist)
import bigchaindb
from bigchaindb import backend, processes
from bigchaindb.backend import schema
from bigchaindb.backend.admin import (set_replicas, set_shards, add_replicas,
                                      remove_replicas)
from bigchaindb.backend.exceptions import OperationError
from bigchaindb.commands import utils
from bigchaindb.commands.messages import (
    CANNOT_START_KEYPAIR_NOT_FOUND,
    RETHINKDB_STARTUP_ERROR,
)
from bigchaindb.commands.utils import (
    configure_bigchaindb, start_logging_process, input_on_stderr)


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
    private_key = config['keypair']['private']
    config['keypair']['private'] = 'x' * 45 if private_key else None
    print(json.dumps(config, indent=4, sort_keys=True))


def run_configure(args, skip_if_exists=False):
    """Run a script to configure the current node.

    Args:
        skip_if_exists (bool): skip the function if a config file already exists
    """
    config_path = args.config or bigchaindb.config_utils.CONFIG_DEFAULT_PATH

    config_file_exists = False
    # if the config path is `-` then it's stdout
    if config_path != '-':
        config_file_exists = os.path.exists(config_path)

    if config_file_exists and skip_if_exists:
        return

    if config_file_exists and not args.yes:
        want = input_on_stderr('Config file `{}` exists, do you want to '
                               'override it? (cannot be undone) [y/N]: '.format(config_path))
        if want != 'y':
            return

    conf = copy.deepcopy(bigchaindb.config)

    # Patch the default configuration with the new values
    conf = bigchaindb.config_utils.update(
            conf,
            bigchaindb.config_utils.env_config(bigchaindb.config))

    print('Generating keypair', file=sys.stderr)
    conf['keypair']['private'], conf['keypair']['public'] = \
        crypto.generate_key_pair()

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

        val = conf['backlog_reassign_delay']
        conf['backlog_reassign_delay'] = input_on_stderr(
            'Stale transaction reassignment delay (in seconds)? (default `{}`): '.format(val), val)

    if config_path != '-':
        bigchaindb.config_utils.write_config(conf, config_path)
    else:
        print(json.dumps(conf, indent=4, sort_keys=True))
    print('Configuration written to {}'.format(config_path), file=sys.stderr)
    print('Ready to go!', file=sys.stderr)


@configure_bigchaindb
def run_export_my_pubkey(args):
    """Export this node's public key to standard output
    """
    pubkey = bigchaindb.config['keypair']['public']
    if pubkey is not None:
        print(pubkey)
    else:
        sys.exit("This node's public key wasn't set anywhere "
                 "so it can't be exported")
        # raises SystemExit exception
        # message is sent to stderr
        # exits with exit code 1 (signals tha an error happened)


def _run_init():
    # Try to access the keypair, throws an exception if it does not exist
    b = bigchaindb.Bigchain()

    schema.init_database(connection=b.connection)

    b.create_genesis_block()
    logger.info('Genesis block created.')


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


@configure_bigchaindb
@start_logging_process
def run_start(args):
    """Start the processes to run the node"""
    logger.info('BigchainDB Version %s', bigchaindb.__version__)

    if args.allow_temp_keypair:
        if not (bigchaindb.config['keypair']['private'] or
                bigchaindb.config['keypair']['public']):

            private_key, public_key = crypto.generate_key_pair()
            bigchaindb.config['keypair']['private'] = private_key
            bigchaindb.config['keypair']['public'] = public_key
        else:
            logger.warning('Keypair found, no need to create one on the fly.')

    if args.start_rethinkdb:
        try:
            proc = utils.start_rethinkdb()
        except StartupError as e:
            sys.exit(RETHINKDB_STARTUP_ERROR.format(e))
        logger.info('RethinkDB started with PID %s' % proc.pid)

    try:
        if not args.skip_initialize_database:
            logger.info('Initializing database')
            _run_init()
    except DatabaseAlreadyExists:
        pass
    except KeypairNotFoundException:
        sys.exit(CANNOT_START_KEYPAIR_NOT_FOUND)

    logger.info('Starting BigchainDB main process with public key %s',
                bigchaindb.config['keypair']['public'])
    processes.start()


@configure_bigchaindb
def run_set_shards(args):
    conn = backend.connect()
    try:
        set_shards(conn, shards=args.num_shards)
    except OperationError as e:
        sys.exit(str(e))


@configure_bigchaindb
def run_set_replicas(args):
    conn = backend.connect()
    try:
        set_replicas(conn, replicas=args.num_replicas)
    except OperationError as e:
        sys.exit(str(e))


@configure_bigchaindb
def run_add_replicas(args):
    # Note: This command is specific to MongoDB
    conn = backend.connect()

    try:
        add_replicas(conn, args.replicas)
    except (OperationError, NotImplementedError) as e:
        sys.exit(str(e))
    else:
        print('Added {} to the replicaset.'.format(args.replicas))


@configure_bigchaindb
def run_remove_replicas(args):
    # Note: This command is specific to MongoDB
    conn = backend.connect()

    try:
        remove_replicas(conn, args.replicas)
    except (OperationError, NotImplementedError) as e:
        sys.exit(str(e))
    else:
        print('Removed {} from the replicaset.'.format(args.replicas))


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
                                          help='Prepare the config file '
                                               'and create the node keypair')
    config_parser.add_argument('backend',
                               choices=['rethinkdb', 'mongodb'],
                               help='The backend to use. It can be either '
                                    'rethinkdb or mongodb.')

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
    start_parser = subparsers.add_parser('start',
                                         help='Start BigchainDB')

    start_parser.add_argument('--dev-allow-temp-keypair',
                              dest='allow_temp_keypair',
                              action='store_true',
                              help='Generate a random keypair on start')

    start_parser.add_argument('--dev-start-rethinkdb',
                              dest='start_rethinkdb',
                              action='store_true',
                              help='Run RethinkDB on start')

    start_parser.add_argument('--no-init',
                              dest='skip_initialize_database',
                              default=False,
                              action='store_true',
                              help='Skip database initialization')

    # parser for configuring the number of shards
    sharding_parser = subparsers.add_parser('set-shards',
                                            help='Configure number of shards')

    sharding_parser.add_argument('num_shards', metavar='num_shards',
                                 type=int, default=1,
                                 help='Number of shards')

    # parser for configuring the number of replicas
    replicas_parser = subparsers.add_parser('set-replicas',
                                            help='Configure number of replicas')

    replicas_parser.add_argument('num_replicas', metavar='num_replicas',
                                 type=int, default=1,
                                 help='Number of replicas (i.e. the replication factor)')

    # parser for adding nodes to the replica set
    add_replicas_parser = subparsers.add_parser('add-replicas',
                                                help='Add a set of nodes to the '
                                                     'replica set. This command '
                                                     'is specific to the MongoDB'
                                                     ' backend.')

    add_replicas_parser.add_argument('replicas', nargs='+',
                                     type=utils.mongodb_host,
                                     help='A list of space separated hosts to '
                                          'add to the replicaset. Each host '
                                          'should be in the form `host:port`.')

    # parser for removing nodes from the replica set
    rm_replicas_parser = subparsers.add_parser('remove-replicas',
                                               help='Remove a set of nodes from the '
                                                    'replica set. This command '
                                                    'is specific to the MongoDB'
                                                    ' backend.')

    rm_replicas_parser.add_argument('replicas', nargs='+',
                                    type=utils.mongodb_host,
                                    help='A list of space separated hosts to '
                                         'remove from the replicaset. Each host '
                                         'should be in the form `host:port`.')
    return parser


def main():
    utils.start(create_parser(), sys.argv[1:], globals())
