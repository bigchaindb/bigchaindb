# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest
from copy import deepcopy

from bigchaindb.models import Transaction
from bigchaindb.common.crypto import generate_key_pair
from bigchaindb.common.memoize import to_dict, from_dict


pytestmark = pytest.mark.bdb


def test_memoize_to_dict(b):
    alice = generate_key_pair()
    asset = {
        'data': {'id': 'test_id'},
    }

    assert to_dict.cache_info().hits == 0
    assert to_dict.cache_info().misses == 0

    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=asset,)\
                    .sign([alice.private_key])

    tx.to_dict()

    assert to_dict.cache_info().hits == 0
    assert to_dict.cache_info().misses == 1

    tx.to_dict()
    tx.to_dict()

    assert to_dict.cache_info().hits == 2
    assert to_dict.cache_info().misses == 1


def test_memoize_from_dict(b):
    alice = generate_key_pair()
    asset = {
        'data': {'id': 'test_id'},
    }

    assert from_dict.cache_info().hits == 0
    assert from_dict.cache_info().misses == 0

    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=asset,)\
                    .sign([alice.private_key])
    tx_dict = deepcopy(tx.to_dict())

    Transaction.from_dict(tx_dict)

    assert from_dict.cache_info().hits == 0
    assert from_dict.cache_info().misses == 1

    Transaction.from_dict(tx_dict)
    Transaction.from_dict(tx_dict)

    assert from_dict.cache_info().hits == 2
    assert from_dict.cache_info().misses == 1


def test_memoize_input_valid(b):
    alice = generate_key_pair()
    asset = {
        'data': {'id': 'test_id'},
    }

    assert Transaction._input_valid.cache_info().hits == 0
    assert Transaction._input_valid.cache_info().misses == 0

    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=asset,)\
                    .sign([alice.private_key])

    tx.inputs_valid()

    assert Transaction._input_valid.cache_info().hits == 0
    assert Transaction._input_valid.cache_info().misses == 1

    tx.inputs_valid()
    tx.inputs_valid()

    assert Transaction._input_valid.cache_info().hits == 2
    assert Transaction._input_valid.cache_info().misses == 1
