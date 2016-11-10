import contextlib
import threading
import queue
import multiprocessing as mp

from bigchaindb.common import crypto
from bigchaindb.common.util import serialize


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


# TODO: Rename this function, it's handling fulfillments not conditions
def condition_details_has_owner(condition_details, owner):
    """

    Check if the public_key of owner is in the condition details
    as an Ed25519Fulfillment.public_key

    Args:
        condition_details (dict): dict with condition details
        owner (str): base58 public key of owner

    Returns:
        bool: True if the public key is found in the condition details, False otherwise

    """
    if 'subfulfillments' in condition_details:
        result = condition_details_has_owner(condition_details['subfulfillments'], owner)
        if result:
            return True

    elif isinstance(condition_details, list):
        for subcondition in condition_details:
            result = condition_details_has_owner(subcondition, owner)
            if result:
                return True
    else:
        if 'public_key' in condition_details \
                and owner == condition_details['public_key']:
            return True
    return False


def verify_vote_signature(voters, signed_vote):
    """Verify the signature of a vote

    A valid vote should have been signed by a voter's private key.

    Args:
        voters (list): voters of the block that is under election
        signed_vote (dict): a vote with the `signature` included.

    Returns:
        bool: True if the signature is correct, False otherwise.
    """

    signature = signed_vote['signature']
    pk_base58 = signed_vote['node_pubkey']

    # immediately return False if the voter is not in the block voter list
    if pk_base58 not in voters:
        return False

    public_key = crypto.PublicKey(pk_base58)
    return public_key.verify(serialize(signed_vote['vote']).encode(), signature)


def is_genesis_block(block):
    """Check if the block is the genesis block.

    Args:
        block (dict | Block): the block to check

    Returns:
        bool: True if the block is the genesis block, False otherwise.
    """

    # we cannot have empty blocks, there will always be at least one
    # element in the list so we can safely refer to it
    # TODO: Remove this try-except and only handle `Block` as input
    try:
        return block.transactions[0].operation == 'GENESIS'
    except AttributeError:
        return block['block']['transactions'][0]['transaction']['operation'] == 'GENESIS'
