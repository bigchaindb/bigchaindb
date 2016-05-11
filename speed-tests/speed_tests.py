from line_profiler import LineProfiler

import bigchaindb


def speedtest_validate_transaction():
    # create a transaction
    b = bigchaindb.Bigchain()
    tx = b.create_transaction(b.me, b.me, None, 'CREATE')
    tx_signed = b.sign_transaction(tx, b.me_private)

    # setup the profiler
    profiler = LineProfiler()
    profiler.enable_by_count()
    profiler.add_function(bigchaindb.Bigchain.validate_transaction)

    # validate_transaction 1000 times
    for i in range(1000):
        b.validate_transaction(tx_signed)

    profiler.print_stats()
