"""Utility functions and basic common arguments
for ``argparse.ArgumentParser``.
"""

import argparse
import multiprocessing as mp
import subprocess

import rethinkdb as r

import bigchaindb
from bigchaindb.exceptions import StartupError
from bigchaindb import db
from bigchaindb.version import __version__


def find_rethinkdb_host():
    """Utility function to find the bigchainDB host
    linked by docker with ``--link <container_name>`
    DISCLAIMER: This is a really dummy function, but should work as long as --link
    option in docker maintains its consistency (and the container name is called ``bigchaindb``

    Returns:
        IP Address of the host machine plus the default port to connect
    """
    default_port = '29015'

    with open('/etc/hosts', encoding='utf-8') as fin:
        for line in fin:
            if line.find('bigchaindb') != -1:
                fin.close()
                return line.split("\t")[0] + ":" + default_port
        fin.close()
        raise StartupError('Expected default hosts format for docker simple container. '
                           'Does your linked machine has a different name then `bigchaindb`?')


def start_rethinkdb(join_address=None):
    """Start RethinkDB as a child process and wait for it to be
    available.

    Args:
        join_address (string): starts rethink db joining an existent node if provided

    Raises:
        ``bigchaindb.exceptions.StartupError`` if RethinkDB cannot
        be started.
    """

    def_args = ['rethinkdb', '--bind', 'all']

    if join_address is not None:
        def_args += ['--join', join_address]

    proc = subprocess.Popen(def_args,
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
                conn = db.get_conn()
                # Before checking if the db is ready, we need to query
                # the server to check if it contains that db
                if r.db_list().contains(dbname).run(conn):
                    r.db(dbname).wait().run(conn)
            except (r.ReqlOpFailedError, r.ReqlDriverError) as exc:
                raise StartupError('Error waiting for the database `{}` '
                                   'to be ready'.format(dbname)) from exc

            return proc

    # We are here when we exhaust the stdout of the process.
    # The last `line` contains info about the error.
    raise StartupError(line)


def start(parser, scope):
    """Utility function to execute a subcommand.

    The function will look up in the ``scope``
    if there is a function called ``run_<parser.args.command>``
    and will run it using ``parser.args`` as first positional argument.

    Args:
        parser: an ArgumentParser instance.
        scope (dict): map containing (eventually) the functions to be called.

    Raises:
        NotImplementedError: if ``scope`` doesn't contain a function called
                             ``run_<parser.args.command>``.
    """
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

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

    func(args)


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
