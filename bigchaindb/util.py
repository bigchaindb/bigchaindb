import multiprocessing as mp
import json
import time
from datetime import datetime

from bigchaindb.crypto import hash_data, PrivateKey


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


def serialize(data):
    """Function used to serialize a dict into a JSON formatted string.

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


def timestamp():
    """Function to calculate a UTC timestamp with microsecond precision.

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
            hash_payload = hash_data(serialize(payload))
            data = {
                'hash': hash_payload,
                'payload': payload
            }
        else:
            raise TypeError('`payload` must be an dict instance')

    hash_payload = hash_data(serialize(payload))
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
    tx_hash = hash_data(tx_serialized)

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
    private_key = PrivateKey(private_key)
    signature = private_key.sign(serialize(transaction))
    signed_transaction = transaction.copy()
    signed_transaction.update({'signature': signature})
    return signed_transaction

