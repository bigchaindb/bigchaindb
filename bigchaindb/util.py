import copy
import time
import contextlib
import threading
import queue
import multiprocessing as mp
import uuid

import rapidjson

import cryptoconditions as cc
from cryptoconditions.exceptions import ParsingError

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
    return rapidjson.dumps(data, skipkeys=False, ensure_ascii=False, sort_keys=True)


def deserialize(data):
    """Deserialize a JSON formatted string into a dict.

    Args:
        data (str): JSON formatted string.

    Returns:
        dict: dict resulting from the serialization of a JSON formatted string.
    """

    return rapidjson.loads(data)


def timestamp():
    """The Unix time, rounded to the nearest second.
       See https://en.wikipedia.org/wiki/Unix_time

    Returns:
        str: the Unix time
    """
    return str(round(time.time()))


# TODO: Consider remove the operation (if there are no inputs CREATE else TRANSFER)
def create_tx(owners_before, owners_after, inputs, operation, payload=None):
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
        owners_before (list): base58 encoded public key of the current owners of the asset.
        owners_after (list): base58 encoded public key of the new owners of the digital asset.
        inputs (list): id of the transaction to use as input.
        operation (str): Either `CREATE` or `TRANSFER` operation.
        payload (Optional[dict]): dictionary with information about asset.

    Returns:
        dict: unsigned transaction.


    Raises:
        TypeError: if the optional ``payload`` argument is not a ``dict``.

    Reference:
        {
            "id": "<sha3 hash>",
            "transaction": {
                "version": "transaction version number",
                "fulfillments": [
                        {
                            "owners_before": ["list of <pub-keys>"],
                            "input": {
                                "txid": "<sha3 hash>",
                                "cid": "condition index"
                            },
                            "fulfillment": "fulfillement of condition cid",
                            "fid": "fulfillment index"
                        }
                    ],
                "conditions": [
                        {
                            "owners_after": ["list of <pub-keys>"],
                            "condition": "condition to be met",
                            "cid": "condition index (1-to-1 mapping with fid)"
                        }
                    ],
                "operation": "<string>",
                "timestamp": "<timestamp from client>",
                "data": {
                    "hash": "<SHA3-256 hash hexdigest of payload>",
                    "payload": {
                        "title": "The Winds of Plast",
                        "creator": "Johnathan Plunkett",
                        "IPFS_key": "QmfQ5QAjvg4GtA3wg3adpnDJug8ktA1BxurVqBD8rtgVjP"
                    }
                }
            },
        }
    """
    # validate arguments (owners and inputs should be lists or None)

    # The None case appears on fulfilling a hashlock
    if owners_before is None:
        owners_before = []
    if not isinstance(owners_before, list):
        owners_before = [owners_before]

    # The None case appears on assigning a hashlock
    if owners_after is None:
        owners_after = []
    if not isinstance(owners_after, list):
        owners_after = [owners_after]

    if not isinstance(inputs, list):
        inputs = [inputs]

    # handle payload
    if payload is not None and not isinstance(payload, dict):
        raise TypeError('`payload` must be an dict instance or None')

    data = {
        'uuid': str(uuid.uuid4()),
        'payload': payload
    }

    # handle inputs
    fulfillments = []

    # transfer
    if inputs:
        for fid, tx_input in enumerate(inputs):
            fulfillments.append({
                'owners_before': owners_before,
                'input': tx_input,
                'fulfillment': None,
                'fid': fid
            })
    # create
    else:
        fulfillments.append({
            'owners_before': owners_before,
            'input': None,
            'fulfillment': None,
            'fid': 0
        })

    # handle outputs
    conditions = []
    for fulfillment in fulfillments:

        # threshold condition
        if len(owners_after) > 1:
            condition = cc.ThresholdSha256Fulfillment(threshold=len(owners_after))
            for owner_after in owners_after:
                condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=owner_after))

        # simple signature condition
        elif len(owners_after) == 1:
            condition = cc.Ed25519Fulfillment(public_key=owners_after[0])

        # to be added later (hashlock conditions)
        else:
            condition = None

        if condition:
            conditions.append({
                'owners_after': owners_after,
                'condition': {
                    'details': condition.to_dict(),
                    'uri': condition.condition_uri
                },
                'cid': fulfillment['fid']
            })

    tx = {
        'version': 1,
        'fulfillments': fulfillments,
        'conditions': conditions,
        'operation': operation,
        'timestamp': timestamp(),
        'data': data
    }

    # serialize and convert to bytes
    tx_hash = get_hash_data(tx)

    # create the transaction
    transaction = {
        'id': tx_hash,
        'transaction': tx
    }

    return transaction


def sign_tx(transaction, signing_keys, bigchain=None):
    """Sign a transaction

    A transaction signed with the `owner_before` corresponding private key.

    Args:
        transaction (dict): transaction to sign.
        signing_keys (list): list of base58 encoded private keys to create the fulfillments of the transaction.
        bigchain (obj): bigchain instance used to get the details of the previous transaction outputs. Useful
                        if the `Bigchain` instance was instantiated with parameters that override the config file.

    Returns:
        dict: transaction with the `fulfillment` fields populated.

    """
    # validate sk
    if not isinstance(signing_keys, list):
        signing_keys = [signing_keys]

    # create a mapping between sk and vk so that we can match the private key to the owners_before
    key_pairs = {}
    for sk in signing_keys:
        signing_key = crypto.SigningKey(sk)
        vk = signing_key.get_verifying_key().to_ascii().decode()
        key_pairs[vk] = signing_key

    tx = copy.deepcopy(transaction)

    bigchain = bigchain if bigchain is not None else bigchaindb.Bigchain()

    for fulfillment in tx['transaction']['fulfillments']:
        fulfillment_message = get_fulfillment_message(transaction, fulfillment)
        # TODO: avoid instantiation, pass as argument!
        input_condition = get_input_condition(bigchain, fulfillment)
        parsed_fulfillment = cc.Fulfillment.from_dict(input_condition['condition']['details'])
        # for the case in which the type of fulfillment is not covered by this method
        parsed_fulfillment_signed = parsed_fulfillment

        # single current owner
        if isinstance(parsed_fulfillment, cc.Ed25519Fulfillment):
            parsed_fulfillment_signed = fulfill_simple_signature_fulfillment(fulfillment,
                                                                             parsed_fulfillment,
                                                                             fulfillment_message,
                                                                             key_pairs)
        # multiple current owners
        elif isinstance(parsed_fulfillment, cc.ThresholdSha256Fulfillment):
            parsed_fulfillment_signed = fulfill_threshold_signature_fulfillment(fulfillment,
                                                                                parsed_fulfillment,
                                                                                fulfillment_message,
                                                                                key_pairs)

        signed_fulfillment = parsed_fulfillment_signed.serialize_uri()
        fulfillment.update({'fulfillment': signed_fulfillment})

    return tx


def fulfill_simple_signature_fulfillment(fulfillment, parsed_fulfillment, fulfillment_message, key_pairs):
    """Fulfill a cryptoconditions.Ed25519Fulfillment

        Args:
            fulfillment (dict): BigchainDB fulfillment to fulfill.
            parsed_fulfillment (cryptoconditions.Ed25519Fulfillment): cryptoconditions.Ed25519Fulfillment instance.
            fulfillment_message (dict): message to sign.
            key_pairs (dict): dictionary of (public_key, private_key) pairs.

        Returns:
            object: fulfilled cryptoconditions.Ed25519Fulfillment

        """
    owner_before = fulfillment['owners_before'][0]

    try:
        parsed_fulfillment.sign(serialize(fulfillment_message), key_pairs[owner_before])
    except KeyError:
        raise exceptions.KeypairMismatchException('Public key {} is not a pair to any of the private keys'
                                                  .format(owner_before))

    return parsed_fulfillment


def fulfill_threshold_signature_fulfillment(fulfillment, parsed_fulfillment, fulfillment_message, key_pairs):
    """Fulfill a cryptoconditions.ThresholdSha256Fulfillment

        Args:
            fulfillment (dict): BigchainDB fulfillment to fulfill.
            parsed_fulfillment (cryptoconditions.ThresholdSha256Fulfillment): cryptoconditions.ThresholdSha256Fulfillment instance.
            fulfillment_message (dict): message to sign.
            key_pairs (dict): dictionary of (public_key, private_key) pairs.

        Returns:
            object: fulfilled cryptoconditions.ThresholdSha256Fulfillment

        """
    parsed_fulfillment_copy = copy.deepcopy(parsed_fulfillment)
    parsed_fulfillment.subconditions = []

    for owner_before in fulfillment['owners_before']:
        try:
            subfulfillment = parsed_fulfillment_copy.get_subcondition_from_vk(owner_before)[0]
        except IndexError:
            raise exceptions.KeypairMismatchException(
                'Public key {} cannot be found in the fulfillment'.format(owner_before))
        try:
            private_key = key_pairs[owner_before]
        except KeyError:
            raise exceptions.KeypairMismatchException(
                'Public key {} is not a pair to any of the private keys'.format(owner_before))

        subfulfillment.sign(serialize(fulfillment_message), private_key)
        parsed_fulfillment.add_subfulfillment(subfulfillment)

    return parsed_fulfillment


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


def validate_fulfillments(signed_transaction):
    """Verify the signature of a transaction

    A valid transaction should have been signed `owner_before` corresponding private key.

    Args:
        signed_transaction (dict): a transaction with the `signature` included.

    Returns:
        bool: True if the signature is correct, False otherwise.
    """
    for fulfillment in signed_transaction['transaction']['fulfillments']:
        fulfillment_message = get_fulfillment_message(signed_transaction, fulfillment)
        try:
            parsed_fulfillment = cc.Fulfillment.from_uri(fulfillment['fulfillment'])
        except (TypeError, ValueError, ParsingError):
            return False

        # TODO: might already break on a False here
        is_valid = parsed_fulfillment.validate(message=serialize(fulfillment_message),
                                               now=timestamp())

        # if transaction has an input (i.e. not a `CREATE` transaction)
        # TODO: avoid instantiation, pass as argument!
        bigchain = bigchaindb.Bigchain()
        input_condition = get_input_condition(bigchain, fulfillment)
        is_valid = is_valid and parsed_fulfillment.condition_uri == input_condition['condition']['uri']

        if not is_valid:
            return False

    return True


def get_fulfillment_message(transaction, fulfillment, serialized=False):
    """Get the fulfillment message for signing a specific fulfillment in a transaction

    Args:
        transaction (dict): a transaction
        fulfillment (dict): a specific fulfillment (for a condition index) within the transaction
        serialized (Optional[bool]): False returns a dict, True returns a serialized string

    Returns:
        str|dict: fulfillment message
    """
    # data to sign contains common transaction data
    fulfillment_message = {
        'operation': transaction['transaction']['operation'],
        'timestamp': transaction['transaction']['timestamp'],
        'data': transaction['transaction']['data'],
        'version': transaction['transaction']['version'],
        'id': transaction['id']
    }
    # and the condition which needs to be retrieved from the output of a previous transaction
    # or created on the fly it this is a `CREATE` transaction
    fulfillment_message.update({
        'fulfillment': copy.deepcopy(fulfillment),
        'condition': transaction['transaction']['conditions'][fulfillment['fid']]
    })

    # remove any fulfillment, as a fulfillment cannot sign itself
    fulfillment_message['fulfillment']['fulfillment'] = None

    if serialized:
        return serialize(fulfillment_message)
    return fulfillment_message


def get_input_condition(bigchain, fulfillment):
    """

    Args:
        bigchain:
        fulfillment:
    Returns:
    """
    input_tx = fulfillment['input']
    # if `TRANSFER` transaction
    if input_tx:
        # get previous condition
        previous_tx = bigchain.get_transaction(input_tx['txid'])
        conditions = sorted(previous_tx['transaction']['conditions'], key=lambda d: d['cid'])
        return conditions[input_tx['cid']]

    # if `CREATE` transaction
    # there is no previous transaction so we need to create one on the fly
    else:
        owner_before = fulfillment['owners_before'][0]
        condition = cc.Ed25519Fulfillment(public_key=owner_before)

        return {
            'condition': {
                'details': condition.to_dict(),
                'uri': condition.condition_uri
            }
        }


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


def get_hash_data(transaction):
    """ Get the hashed data that (should) correspond to the `transaction['id']`

    Args:
        transaction (dict): the transaction to be hashed

    Returns:
        str: the hash of the transaction
    """
    tx = copy.deepcopy(transaction)
    if 'transaction' in tx:
        tx = tx['transaction']

    # remove the fulfillment messages (signatures)
    for fulfillment in tx['fulfillments']:
        fulfillment['fulfillment'] = None

    return crypto.hash_data(serialize(tx))


def verify_vote_signature(block, signed_vote):
    """Verify the signature of a vote

    A valid vote should have been signed `owner_before` corresponding private key.

    Args:
        block (dict): block under election
        signed_vote (dict): a vote with the `signature` included.

    Returns:
        bool: True if the signature is correct, False otherwise.
    """

    signature = signed_vote['signature']
    vk_base58 = signed_vote['node_pubkey']

    # immediately return False if the voter is not in the block voter list
    if vk_base58 not in block['block']['voters']:
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

