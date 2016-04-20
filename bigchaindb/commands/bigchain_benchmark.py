"""Command line interface for the `bigchaindb-benchmark` command."""

import logging
import argparse

import logstats

import bigchaindb
import bigchaindb.config_utils
from bigchaindb.util import ProcessGroup
from bigchaindb.client import temp_client
from bigchaindb.commands.utils import base_parser, start


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _run_load(tx_left, stats):
    logstats.thread.start(stats)
    client = temp_client()
    # b = bigchaindb.Bigchain()

    while True:
        tx = client.create()

        stats['transactions'] += 1

        if tx_left is not None:
            tx_left -= 1
            if tx_left == 0:
                break


def run_load(args):
    bigchaindb.config_utils.autoconfigure(filename=args.config, force=True)
    logger.info('Starting %s processes', args.multiprocess)
    stats = logstats.Logstats()
    logstats.thread.start(stats)

    tx_left = None
    if args.count > 0:
        tx_left = int(args.count / args.multiprocess)

    workers = ProcessGroup(concurrency=args.multiprocess,
                           target=_run_load,
                           args=(tx_left, stats.get_child()))
    workers.start()


def main():
    parser = argparse.ArgumentParser(description='Benchmark your bigchain federation.',
                                     parents=[base_parser])

    # all the commands are contained in the subparsers object,
    # the command selected by the user will be stored in `args.command`
    # that is used by the `main` function to select which other
    # function to call.
    subparsers = parser.add_subparsers(title='Commands',
                                       dest='command')

    # parser for database level commands
    load_parser = subparsers.add_parser('load',
                                        help='Write transactions to the backlog')

    load_parser.add_argument('-m', '--multiprocess',
                             nargs='?',
                             type=int,
                             default=False,
                             help='Spawn multiple processes to run the command, '
                                  'if no value is provided, the number of processes '
                                  'is equal to the number of cores of the host machine')

    load_parser.add_argument('-c', '--count',
                             default=0,
                             type=int,
                             help='Number of transactions to push. If the parameter -m '
                                  'is set, the count is distributed equally to all the '
                                  'processes')

    start(parser, globals())

if __name__ == '__main__':
    main()
