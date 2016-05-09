import sys
import multiprocessing as mp
import uuid
from bigchaindb import Bigchain
from bigchaindb.util import ProcessGroup


def create_write_transaction(tx_left):
    b = Bigchain()
    while tx_left > 0:
        # use uuid to prevent duplicate transactions (transactions with the same hash)
        tx = b.create_transaction(b.me, b.me, None, 'CREATE', payload={'msg': str(uuid.uuid4())})
        tx_signed = b.sign_transaction(tx, b.me_private)
        b.write_transaction(tx_signed)
        tx_left -= 1


def add_to_backlog(num_transactions=10000):
    tx_left = num_transactions // mp.cpu_count()
    workers = ProcessGroup(target=create_write_transaction, args=(tx_left,))
    workers.start()


if __name__ == '__main__':
    add_to_backlog(int(sys.argv[1]))

