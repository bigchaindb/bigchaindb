import multiprocessing as mp
import uuid
import json
import argparse

from os.path import expanduser

from bigchaindb import Bigchain
from bigchaindb.util import ProcessGroup
from bigchaindb.commands import utils


def create_write_transaction(tx_left):
    b = Bigchain()
    while tx_left > 0:
        # use uuid to prevent duplicate transactions (transactions with the same hash)
        tx = b.create_transaction(b.me, b.me, None, 'CREATE',
                                  payload={'msg': str(uuid.uuid4())})
        tx_signed = b.sign_transaction(tx, b.me_private)
        b.write_transaction(tx_signed)
        tx_left -= 1


def run_add_backlog(args):
    tx_left = args.num_transactions // mp.cpu_count()
    workers = ProcessGroup(target=create_write_transaction, args=(tx_left,))
    workers.start()


def run_set_statsd_host(args):
    with open(expanduser('~') + '/.bigchaindb', 'r') as f:
        conf = json.load(f)

    conf['statsd']['host'] = args.statsd_host
    with open(expanduser('~') + '/.bigchaindb', 'w') as f:
        json.dump(conf, f)


def main():
    parser = argparse.ArgumentParser(description='BigchainDB benchmarking utils')
    subparsers = parser.add_subparsers(title='Commands', dest='command')

    # add transactions to backlog
    backlog_parser = subparsers.add_parser('add-backlog',
                                           help='Add transactions to the backlog')
    backlog_parser.add_argument('num_transactions', metavar='num_transactions', type=int, default=0,
                                help='Number of transactions to add to the backlog')

    # set statsd host
    statsd_parser = subparsers.add_parser('set-statsd-host',
                                          help='Set statsd host')
    statsd_parser.add_argument('statsd_host', metavar='statsd_host', default='localhost',
                               help='Hostname of the statsd server')

    utils.start(parser, globals())


if __name__ == '__main__':
    main()

