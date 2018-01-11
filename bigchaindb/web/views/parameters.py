import re


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
        return 'broadcast_tx_async'
    if mode == 'sync':
        return 'broadcast_tx_sync'
    if mode == 'commit':
        return 'broadcast_tx_commit'
    raise ValueError('Mode must be "async", "sync" or "commit"')
