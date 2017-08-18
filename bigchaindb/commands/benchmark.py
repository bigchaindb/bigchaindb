import sys
import argparse
import logging
import webbrowser

import coloredlogs

from bigchaindb.commands import utils


logger = logging.getLogger(__name__)


def run_send(args):
    from bigchaindb_driver import BigchainDB
    from bigchaindb_driver.crypto import generate_keypair

    alice = generate_keypair()
    bdb = BigchainDB(args.peer)
    asset = None

    if args.size:
        asset = {'data': {'_': 'x' * args.size}}

    prepared_creation_tx = bdb.transactions.prepare(
            operation='CREATE',
            signers=alice.public_key,
            asset=asset,
            metadata=None)

    fulfilled_creation_tx = bdb.transactions.fulfill(
            prepared_creation_tx,
            private_keys=alice.private_key)

    sent_creation_tx = bdb.transactions.send(fulfilled_creation_tx)
    logger.info('Create transaction sent. Id: %s', sent_creation_tx['id'])

    if args.open:
        webbrowser.open('{}/api/v1/transactions/{}'.format(args.peer, sent_creation_tx['id']))


def create_parser():
    parser = argparse.ArgumentParser(
            description='[experimental] Benchmarking tools for BigchainDB.')

    parser.add_argument('-l', '--log-level',
                        default='INFO')

    parser.add_argument('-p', '--peer',
                        default='http://localhost:9984')

    # all the commands are contained in the subparsers object,
    # the command selected by the user will be stored in `args.command`
    # that is used by the `main` function to select which other
    # function to call.
    subparsers = parser.add_subparsers(title='Commands',
                                       dest='command')

    send_parser = subparsers.add_parser('send',
                                        help='Send a single create transaction '
                                        'from a random keypair')

    send_parser.add_argument('--open',
                             help='Open the transaction in the browser',
                             default=False,
                             action='store_true')

    send_parser.add_argument('--size',
                             help='Asset size in bytes',
                             type=int,
                             default=0)

    return parser


def configure(args):
    coloredlogs.install(level=args.log_level, logger=logger)


def main():
    utils.start(create_parser(),
                sys.argv[1:],
                globals(),
                callback_before=configure)
