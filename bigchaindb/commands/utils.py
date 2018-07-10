"""Utility functions and basic common arguments
for ``argparse.ArgumentParser``.
"""

import argparse
import builtins
import functools
import multiprocessing as mp
import sys

import bigchaindb
import bigchaindb.config_utils
from bigchaindb.version import __version__


def configure_bigchaindb(command):
    """Decorator to be used by command line functions, such that the
    configuration of bigchaindb is performed before the execution of
    the command.

    Args:
        command: The command to decorate.

    Returns:
        The command wrapper function.

    """
    @functools.wraps(command)
    def configure(args):
        config_from_cmdline = None
        try:
            if args.log_level is not None:
                config_from_cmdline = {
                    'log': {
                        'level_console': args.log_level,
                        'level_logfile': args.log_level,
                    },
                    'server': {'loglevel': args.log_level},
                }
        except AttributeError:
            pass
        bigchaindb.config_utils.autoconfigure(
            filename=args.config, config=config_from_cmdline, force=True)
        command(args)

    return configure


def _convert(value, default=None, convert=None):
    def convert_bool(value):
        if value.lower() in ('true', 't', 'yes', 'y'):
            return True
        if value.lower() in ('false', 'f', 'no', 'n'):
            return False
        raise ValueError('{} cannot be converted to bool'.format(value))

    if value == '':
        value = None

    if convert is None:
        if default is not None:
            convert = type(default)
        else:
            convert = str

    if convert == bool:
        convert = convert_bool

    if value is None:
        return default
    else:
        return convert(value)


# We need this because `input` always prints on stdout, while it should print
# to stderr. It's a very old bug, check it out here:
# - https://bugs.python.org/issue1927
def input_on_stderr(prompt='', default=None, convert=None):
    """Output a string to stderr and wait for input.

    Args:
        prompt (str): the message to display.
        default: the default value to return if the user
            leaves the field empty
        convert (callable): a callable to be used to convert
            the value the user inserted. If None, the type of
            ``default`` will be used.
    """

    print(prompt, end='', file=sys.stderr)
    value = builtins.input()
    return _convert(value, default, convert)


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


base_parser = argparse.ArgumentParser(add_help=False, prog='bigchaindb')

base_parser.add_argument('-c', '--config',
                         help='Specify the location of the configuration file '
                              '(use "-" for stdout)')

# NOTE: this flag should not have any default value because that will override
# the environment variables provided to configure the logger.
base_parser.add_argument('-l', '--log-level',
                         type=str.upper,  # convert to uppercase for comparison to choices
                         choices=['DEBUG', 'BENCHMARK', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                         help='Log level')

base_parser.add_argument('-y', '--yes', '--yes-please',
                         action='store_true',
                         help='Assume "yes" as answer to all prompts and run '
                              'non-interactively')

base_parser.add_argument('-v', '--version',
                         action='version',
                         version='%(prog)s {}'.format(__version__))
