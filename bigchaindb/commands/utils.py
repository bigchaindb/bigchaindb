"""Utility functions and basic common arguments
for ``argparse.ArgumentParser``.
"""

import argparse
import multiprocessing as mp
import subprocess

import rethinkdb as r
from pymongo import uri_parser

import bigchaindb
from bigchaindb import backend
from bigchaindb.common.exceptions import StartupError
from bigchaindb.version import __version__


def start_rethinkdb():
    """Start RethinkDB as a child process and wait for it to be
    available.

    Raises:
        :class:`~bigchaindb.common.exceptions.StartupError` if
            RethinkDB cannot be started.
    """

    proc = subprocess.Popen(['rethinkdb', '--bind', 'all'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)

    dbname = bigchaindb.config['database']['name']
    line = ''

    for line in proc.stdout:
        if line.startswith('Server ready'):

            # FIXME: seems like tables are not ready when the server is ready,
            #        that's why we need to query RethinkDB to know the state
            #        of the database. This code assumes the tables are ready
            #        when the database is ready. This seems a valid assumption.
            try:
                conn = backend.connect()
                # Before checking if the db is ready, we need to query
                # the server to check if it contains that db
                if conn.run(r.db_list().contains(dbname)):
                    conn.run(r.db(dbname).wait())
            except (r.ReqlOpFailedError, r.ReqlDriverError) as exc:
                raise StartupError('Error waiting for the database `{}` '
                                   'to be ready'.format(dbname)) from exc
            return proc

    # We are here when we exhaust the stdout of the process.
    # The last `line` contains info about the error.
    raise StartupError(line)


def start(parser, argv, scope):
    """Utility function to execute a subcommand.

    The function will look up in the ``scope``
    if there is a function called ``run_<parser.args.command>``
    and will run it using ``parser.args`` as first positional argument.

    Args:
        parser: an ArgumentParser instance.
        argv: the list of command line arguments without the script name.
        scope (dict): map containing (eventually) the functions to be called.

    Raises:
        NotImplementedError: if ``scope`` doesn't contain a function called
                             ``run_<parser.args.command>``.
    """
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        raise SystemExit()

    # look up in the current scope for a function called 'run_<command>'
    # replacing all the dashes '-' with the lowercase character '_'
    func = scope.get('run_' + args.command.replace('-', '_'))

    # if no command has been found, raise a `NotImplementedError`
    if not func:
        raise NotImplementedError('Command `{}` not yet implemented'.
                                  format(args.command))

    args.multiprocess = getattr(args, 'multiprocess', False)

    if args.multiprocess is False:
        args.multiprocess = 1
    elif args.multiprocess is None:
        args.multiprocess = mp.cpu_count()

    return func(args)


def mongodb_host(host):
    """Utility function that works as a type for mongodb ``host`` args.

    This function validates the ``host`` args provided by to the
    ``add-replicas`` and ``remove-replicas`` commands and checks if each arg
    is in the form "host:port"

    Args:
        host (str): A string containing hostname and port (e.g. "host:port")

    Raises:
        ArgumentTypeError: if it fails to parse the argument
    """
    # check if mongodb can parse the host
    try:
        hostname, port = uri_parser.parse_host(host, default_port=None)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(exc.args[0])

    # we do require the port to be provided.
    if port is None or hostname == '':
        raise argparse.ArgumentTypeError('expected host in the form '
                                         '`host:port`. Got `{}` instead.'
                                         .format(host))

    return host


base_parser = argparse.ArgumentParser(add_help=False, prog='bigchaindb')

base_parser.add_argument('-c', '--config',
                         help='Specify the location of the configuration file '
                              '(use "-" for stdout)')

base_parser.add_argument('-y', '--yes', '--yes-please',
                         action='store_true',
                         help='Assume "yes" as answer to all prompts and run '
                              'non-interactively')

base_parser.add_argument('-v', '--version',
                         action='version',
                         version='%(prog)s {}'.format(__version__))
