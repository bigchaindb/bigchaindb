import sys
import math
import time
import requests
import subprocess
import multiprocessing


def main():
    cmd('docker-compose up -d mdb')
    cmd('docker-compose up -d bdb')
    cmd('docker-compose up -d graphite')

    out = cmd('docker-compose port graphite 80', capture=True)
    graphite_web = 'http://localhost:%s/' % out.strip().split(':')[1]
    print('Graphite web interface at: ' + graphite_web)

    start = time.time()

    cmd('docker-compose exec bdb python %s load' % sys.argv[0])

    mins = math.ceil((time.time() - start) / 60) + 1

    graph_url = graphite_web + 'render/?width=900&height=600&_salt=1495462891.335&target=stats.pipelines.block.throughput&target=stats.pipelines.vote.throughput&target=stats.web.tx.post&from=-%sminutes' % mins  # noqa

    print(graph_url)


def load():
    from bigchaindb.core import Bigchain
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.common.transaction import Transaction

    def transactions():
        priv, pub = generate_key_pair()
        tx = Transaction.create([pub], [([pub], 1)])
        while True:
            i = yield tx.to_dict()
            tx.asset = {'data': {'n': i}}
            tx.sign([priv])

    def wait_for_up():
        print('Waiting for server to start... ', end='')
        while True:
            try:
                requests.get('http://localhost:9984/')
                break
            except requests.ConnectionError:
                time.sleep(0.1)
        print('Ok')

    def post_txs():
        txs = transactions()
        txs.send(None)
        try:
            with requests.Session() as session:
                while True:
                    i = tx_queue.get()
                    if i is None:
                        break
                    tx = txs.send(i)
                    res = session.post('http://localhost:9984/api/v1/transactions/', json=tx)
                    assert res.status_code == 202
        except KeyboardInterrupt:
            pass

    wait_for_up()
    num_clients = 30
    test_time = 60
    tx_queue = multiprocessing.Queue(maxsize=num_clients)
    txn = 0
    b = Bigchain()

    start_time = time.time()

    for i in range(num_clients):
        multiprocessing.Process(target=post_txs).start()

    print('Sending transactions')
    while time.time() - start_time < test_time:
        # Post 500 transactions to the server
        for i in range(500):
            tx_queue.put(txn)
            txn += 1
        print(txn)
        while True:
            # Wait for the server to reduce the backlog to below
            # 10000 transactions. The expectation is that 10000 transactions
            # will not be processed faster than a further 500 transactions can
            # be posted, but nonetheless will be processed within a few seconds.
            # This keeps the test from running on and keeps the transactions from
            # being considered stale.
            count = b.connection.db.backlog.count()
            if count > 10000:
                time.sleep(0.2)
            else:
                break

    for i in range(num_clients):
        tx_queue.put(None)

    print('Waiting to clear backlog')
    while True:
        bl = b.connection.db.backlog.count()
        if bl == 0:
            break
        print(bl)
        time.sleep(1)

    print('Waiting for all votes to come in')
    while True:
        blocks = b.connection.db.bigchain.count()
        votes = b.connection.db.votes.count()
        if blocks == votes + 1:
            break
        print('%s blocks, %s votes' % (blocks, votes))
        time.sleep(3)

    print('Finished')


def cmd(command, capture=False):
    stdout = subprocess.PIPE if capture else None
    args = ['bash', '-c', command]
    proc = subprocess.Popen(args, stdout=stdout)
    assert not proc.wait()
    return capture and proc.stdout.read().decode()


if sys.argv[1:] == ['load']:
    load()
else:
    main()
