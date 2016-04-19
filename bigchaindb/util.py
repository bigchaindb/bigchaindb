
import json
import time
import contextlib
import threading
import queue
import multiprocessing as mp
from datetime import datetime

import bigchaindb
from bigchaindb import exceptions
from bigchaindb import crypto


class ProcessGroup(object):

    def __init__(self, concurrency=None, group=None, target=None, name=None,
                 args=None, kwargs=None, daemon=None):
        self.concurrency = concurrency or mp.cpu_count()
        self.group = group
        self.target = target
        self.name = name
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.daemon = daemon
        self.processes = []

    def start(self):
        for i in range(self.concurrency):
            proc = mp.Process(group=self.group, target=self.target,
                              name=self.name, args=self.args,
                              kwargs=self.kwargs, daemon=self.daemon)
            proc.start()
            self.processes.append(proc)


# Inspired by:
# - http://stackoverflow.com/a/24741694/597097
def pool(builder, size, timeout=None):
    """Create a pool that imposes a limit on the number of stored
    instances.

    Args:
        builder: a function to build an instance.
        size: the size of the pool.
        timeout(Optional[float]): the seconds to wait before raising
            a ``queue.Empty`` exception if no instances are available
            within that time.
    Raises:
        If ``timeout`` is defined but the request is taking longer
        than the specified time, the context manager will raise
        a ``queue.Empty`` exception.

    Returns:
        A context manager that can be used with the ``with``
        statement.

    """

    lock = threading.Lock()
    local_pool = queue.Queue()
    current_size = 0

    @contextlib.contextmanager
    def pooled():
        nonlocal current_size
        instance = None

        # If we still have free slots, then we have room to create new
        # instances.
        if current_size < size:
            with lock:
                # We need to check again if we have slots available, since
                # the situation might be different after acquiring the lock
                if current_size < size:
                    current_size += 1
                    instance = builder()

        # Watchout: current_size can be equal to size if the previous part of
        # the function has been executed, that's why we need to check if the
        # instance is None.
        if instance is None:
            instance = local_pool.get(timeout=timeout)

        yield instance

        local_pool.put(instance)

    return pooled


def serialize(data):
    """Serialize a dict into a JSON formatted string.

    This function enforces rules like the separator and order of keys. This ensures that all dicts
    are serialized in the same way.

    This is specially important for hashing data. We need to make sure that everyone serializes their data
    in the same way so that we do not have hash mismatches for the same structure due to serialization
    differences.

    Args:
        data (dict): dict to serialize

    Returns:
        str: JSON formatted string

    """
    return json.dumps(data, skipkeys=False, ensure_ascii=False,
                      separators=(',', ':'), sort_keys=True)


def deserialize(data):
    """Deserialize a JSON formatted string into a dict.

    Args:
        data (str): JSON formatted string.

    Returns:
        dict: dict resulting from the serialization of a JSON formatted string.
    """

    return json.loads(data, encoding="utf-8")


def timestamp():
    """Calculate a UTC timestamp with microsecond precision.

    Returns:
        str: UTC timestamp.

    """
    dt = datetime.utcnow()
    return "{0:.6f}".format(time.mktime(dt.timetuple()) + dt.microsecond / 1e6)


def create_tx(current_owner, new_owner, tx_input, operation, payload=None):
    """Create a new transaction

    A transaction in the bigchain is a transfer of a digital asset between two entities represented
    by public keys.

    Currently the bigchain supports two types of operations:

        `CREATE` - Only federation nodes are allowed to use this operation. In a create operation
        a federation node creates a digital asset in the bigchain and assigns that asset to a public
        key. The owner of the private key can then decided to transfer this digital asset by using the
        `transaction id` of the transaction as an input in a `TRANSFER` transaction.

        `TRANSFER` - A transfer operation allows for a transfer of the digital assets between entities.

    Args:
        current_owner (str): base58 encoded public key of the current owner of the asset.
        new_owner (str): base58 encoded public key of the new owner of the digital asset.
        tx_input (str): id of the transaction to use as input.
        operation (str): Either `CREATE` or `TRANSFER` operation.
        payload (Optional[dict]): dictionary with information about asset.

    Returns:
        dict: unsigned transaction.


    Raises:
        TypeError: if the optional ``payload`` argument is not a ``dict``.
    """

    data = None
    if payload is not None:
        if isinstance(payload, dict):
            hash_payload = crypto.hash_data(serialize(payload))
            data = {
                'hash': hash_payload,
                'payload': payload
            }
        else:
            raise TypeError('`payload` must be an dict instance')

    hash_payload = crypto.hash_data(serialize(payload))
    data = {
        'hash': hash_payload,
        'payload': payload
    }

    tx = {
        'current_owner': current_owner,
        'new_owner': new_owner,
        'input': tx_input,
        'operation': operation,
        'timestamp': timestamp(),
        'data': data
    }

    # serialize and convert to bytes
    tx_serialized = serialize(tx)
    tx_hash = crypto.hash_data(tx_serialized)

    # create the transaction
    transaction = {
        'id': tx_hash,
        'transaction': tx
    }

    return transaction


def sign_tx(transaction, private_key):
    """Sign a transaction

    A transaction signed with the `current_owner` corresponding private key.

    Args:
        transaction (dict): transaction to sign.
        private_key (str): base58 encoded private key to create a signature of the transaction.

    Returns:
        dict: transaction with the `signature` field included.

    """
    private_key = crypto.SigningKey(private_key)
    signature = private_key.sign(serialize(transaction))
    signed_transaction = transaction.copy()
    signed_transaction.update({'signature': signature.decode()})
    return signed_transaction


def create_and_sign_tx(private_key, current_owner, new_owner, tx_input, operation='TRANSFER', payload=None):
    tx = create_tx(current_owner, new_owner, tx_input, operation, payload)
    return sign_tx(tx, private_key)


def check_hash_and_signature(transaction):
    # Check hash of the transaction
    calculated_hash = crypto.hash_data(serialize(transaction['transaction']))
    if calculated_hash != transaction['id']:
        raise exceptions.InvalidHash()

    # Check signature
    if not verify_signature(transaction):
        raise exceptions.InvalidSignature()


def verify_signature(signed_transaction):
    """Verify the signature of a transaction

    A valid transaction should have been signed `current_owner` corresponding private key.

    Args:
        signed_transaction (dict): a transaction with the `signature` included.

    Returns:
        bool: True if the signature is correct, False otherwise.
    """

    data = signed_transaction.copy()

    # if assignee field in the transaction, remove it
    if 'assignee' in data:
        data.pop('assignee')

    signature = data.pop('signature')
    public_key_base58 = signed_transaction['transaction']['current_owner']
    public_key = crypto.VerifyingKey(public_key_base58)
    return public_key.verify(serialize(data), signature)


def transform_create(tx):
    """Change the owner and signature for a ``CREATE`` transaction created by a node"""

    # XXX: the next instruction opens a new connection to the DB, consider using a singleton or a global
    #      if you need a Bigchain instance.
    b = bigchaindb.Bigchain()
    transaction = tx['transaction']
    payload = None
    if transaction['data'] and 'payload' in transaction['data']:
        payload = transaction['data']['payload']
    new_tx = create_tx(b.me, transaction['current_owner'], None, 'CREATE', payload=payload)
    return new_tx

