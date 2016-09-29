import json
import time

import rapidjson
from line_profiler import LineProfiler

import bigchaindb

# BIG TODO: Adjust for new transaction model


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


def speedtest_serialize_block_json():
    # create a block
    b = bigchaindb.Bigchain()
    tx = b.create_transaction(b.me, b.me, None, 'CREATE')
    tx_signed = b.sign_transaction(tx, b.me_private)
    block = b.create_block([tx_signed] * 1000)

    time_start = time.time()
    for _ in range(1000):
        _ = json.dumps(block, skipkeys=False, ensure_ascii=False, sort_keys=True)
    time_elapsed = time.time() - time_start

    print('speedtest_serialize_block_json: {} s'.format(time_elapsed))


def speedtest_serialize_block_rapidjson():
    # create a block
    b = bigchaindb.Bigchain()
    tx = b.create_transaction(b.me, b.me, None, 'CREATE')
    tx_signed = b.sign_transaction(tx, b.me_private)
    block = b.create_block([tx_signed] * 1000)

    time_start = time.time()
    for _ in range(1000):
        _ = rapidjson.dumps(block, skipkeys=False, ensure_ascii=False, sort_keys=True)
    time_elapsed = time.time() - time_start

    print('speedtest_serialize_block_rapidjson: {} s'.format(time_elapsed))


def speedtest_deserialize_block_json():
    # create a block
    b = bigchaindb.Bigchain()
    tx = b.create_transaction(b.me, b.me, None, 'CREATE')
    tx_signed = b.sign_transaction(tx, b.me_private)
    block = b.create_block([tx_signed] * 1000)
    block_serialized = json.dumps(block, skipkeys=False, ensure_ascii=False, sort_keys=True)

    time_start = time.time()
    for _ in range(1000):
        _ = json.loads(block_serialized)
    time_elapsed = time.time() - time_start

    print('speedtest_deserialize_block_json: {} s'.format(time_elapsed))


def speedtest_deserialize_block_rapidjson():
    # create a block
    b = bigchaindb.Bigchain()
    tx = b.create_transaction(b.me, b.me, None, 'CREATE')
    tx_signed = b.sign_transaction(tx, b.me_private)
    block = b.create_block([tx_signed] * 1000)
    block_serialized = rapidjson.dumps(block, skipkeys=False, ensure_ascii=False, sort_keys=True)

    time_start = time.time()
    for _ in range(1000):
        _ = rapidjson.loads(block_serialized)
    time_elapsed = time.time() - time_start

    print('speedtest_deserialize_block_rapidjson: {} s'.format(time_elapsed))


if __name__ == '__main__':
    speedtest_validate_transaction()
    speedtest_serialize_block_json()
    speedtest_serialize_block_rapidjson()
    speedtest_deserialize_block_json()
    speedtest_deserialize_block_rapidjson()
