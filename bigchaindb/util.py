import time
import contextlib
from copy import deepcopy
import threading
import queue
import multiprocessing as mp
import uuid

import rapidjson

from bigchaindb_common import crypto, exceptions
from bigchaindb_common.transaction import Transaction
from bigchaindb_common.util import serialize
import cryptoconditions as cc
from cryptoconditions.exceptions import ParsingError

import bigchaindb


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


# TODO: Replace this with a Block model
def serialize_block(block):
    return serialize(_serialize_txs_block(block))


def _serialize_txs_block(block):
    """Takes a block and serializes its transactions from models to JSON
    """
    # NOTE: Avoid side effects on the block
    block = deepcopy(block)
    try:
        block['block']['transactions'] = [tx.to_dict() for tx
                                          in block['block']['transactions']]
    except KeyError:
        block['transactions'] = [tx.to_dict() for tx in block['transactions']]
    return block


# TODO: Replace this with a Block model
def deserialize_block(block):
    """Takes a block and serializes its transactions from JSON to models
    """
    block['block']['transactions'] = [Transaction.from_dict(tx) for tx
                                      in block['block']['transactions']]
    return block


def create_and_sign_tx(private_key, owner_before, owner_after, tx_input, operation='TRANSFER', payload=None):
    tx = create_tx(owner_before, owner_after, tx_input, operation, payload)
    return sign_tx(tx, private_key)


def check_hash_and_signature(transaction):
    # Check hash of the transaction
    calculated_hash = get_hash_data(transaction)
    if calculated_hash != transaction['id']:
        raise exceptions.InvalidHash()

    # Check signature
    if not validate_fulfillments(transaction):
        raise exceptions.InvalidSignature()


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

    A valid vote should have been signed `owner_before` corresponding private key.

    Args:
        voters (list): voters of the block that is under election
        signed_vote (dict): a vote with the `signature` included.

    Returns:
        bool: True if the signature is correct, False otherwise.
    """

    signature = signed_vote['signature']
    vk_base58 = signed_vote['node_pubkey']

    # immediately return False if the voter is not in the block voter list
    if vk_base58 not in voters:
        return False

    public_key = crypto.VerifyingKey(vk_base58)
    return public_key.verify(serialize(signed_vote['vote']), signature)


def transform_create(tx):
    """Change the owner and signature for a ``CREATE`` transaction created by a node"""

    # XXX: the next instruction opens a new connection to the DB, consider using a singleton or a global
    #      if you need a Bigchain instance.
    b = bigchaindb.Bigchain()
    transaction = tx['transaction']
    payload = None
    if transaction['data'] and 'payload' in transaction['data']:
        payload = transaction['data']['payload']
    new_tx = create_tx(b.me, transaction['fulfillments'][0]['owners_before'], None, 'CREATE', payload=payload)
    return new_tx


def is_genesis_block(block):
    """Check if the block is the genesis block.

    Args:
        block (dict): the block to check

    Returns:
        bool: True if the block is the genesis block, False otherwise.
    """

    # we cannot have empty blocks, there will always be at least one
    # element in the list so we can safely refer to it
    return block['block']['transactions'][0]['transaction']['operation'] == 'GENESIS'
