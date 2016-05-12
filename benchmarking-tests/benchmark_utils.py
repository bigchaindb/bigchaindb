import multiprocessing as mp
import uuid
import json
import argparse
import csv
import time
import logging
import rethinkdb as r

from os.path import expanduser

from bigchaindb import Bigchain
from bigchaindb.util import ProcessGroup
from bigchaindb.commands import utils


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def run_gather_metrics(args):
    # setup a rethinkdb connection
    conn = r.connect(args.bigchaindb_host, 28015, 'bigchain')

    # setup csv writer
    csv_file = open(args.csvfile, 'w')
    csv_writer = csv.writer(csv_file)

    # query for the number of transactions on the backlog
    num_transactions = r.table('backlog').count().run(conn)
    num_transactions_received = 0
    initial_time = None
    logger.info('Starting gathering metrics. {} transasctions in the backlog'.format(num_transactions))
    logger.info('This process should exit automatically. '
                'If this does not happen you can exit at any time using Ctrl-C'
                ' saving all the metrics gathered up to this point.')

    logger.info('\t{:<20} {:<20} {:<20} {:<20}'.format('timestamp', 'tx in block',
                                                     'tx/s', '% complete'))

    # listen to the changefeed
    try:
        for change in r.table('bigchain').changes().run(conn):
            # check only for new blocks
            if change['old_val'] is None:
                block_num_transactions = len(change['new_val']['block']['transactions'])
                time_now = time.time()
                csv_writer.writerow([str(time_now), str(block_num_transactions)])

                # log statistics
                if initial_time is None:
                    initial_time = time_now

                num_transactions_received += block_num_transactions
                elapsed_time = time_now - initial_time
                percent_complete = round((num_transactions_received / num_transactions) * 100)

                if elapsed_time != 0:
                    transactions_per_second = round(num_transactions_received / elapsed_time)
                else:
                    transactions_per_second = float('nan')

                logger.info('\t{:<20} {:<20} {:<20} {:<20}'.format(time_now, block_num_transactions,
                                                                   transactions_per_second, percent_complete))

                if (num_transactions - num_transactions_received) == 0:
                    break
    except KeyboardInterrupt:
        logger.info('Interrupted. Exiting early...')
    finally:
        # close files
        csv_file.close()


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

    # metrics
    metrics_parser = subparsers.add_parser('gather-metrics',
                                           help='Gather metrics to a csv file')

    metrics_parser.add_argument('-b', '--bigchaindb-host',
                                required=True,
                                help='Bigchaindb node hostname to connect to gather cluster metrics')

    metrics_parser.add_argument('-c', '--csvfile',
                                required=True,
                                help='Filename to save the metrics')

    utils.start(parser, globals())


if __name__ == '__main__':
    main()

