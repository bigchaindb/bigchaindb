# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import re

from bigchaindb.common.transaction_mode_types import (BROADCAST_TX_COMMIT,
                                                      BROADCAST_TX_ASYNC,
                                                      BROADCAST_TX_SYNC)


def valid_txid(txid):
    if re.match('^[a-fA-F0-9]{64}$', txid):
        return txid.lower()
    raise ValueError('Invalid hash')


def valid_bool(val):
    val = val.lower()
    if val == 'true':
        return True
    if val == 'false':
        return False
    raise ValueError('Boolean value must be "true" or "false" (lowercase)')


def valid_ed25519(key):
    if (re.match('^[1-9a-zA-Z]{43,44}$', key) and not
       re.match('.*[Il0O]', key)):
        return key
    raise ValueError('Invalid base58 ed25519 key')


def valid_operation(op):
    op = op.upper()
    if op == 'CREATE':
        return 'CREATE'
    if op == 'TRANSFER':
        return 'TRANSFER'
    raise ValueError('Operation must be "CREATE" or "TRANSFER"')


def valid_mode(mode):
    if mode == 'async':
        return BROADCAST_TX_ASYNC
    if mode == 'sync':
        return BROADCAST_TX_SYNC
    if mode == 'commit':
        return BROADCAST_TX_COMMIT
    raise ValueError('Mode must be "async", "sync" or "commit"')
