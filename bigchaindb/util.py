import copy
import json
import time
import multiprocessing as mp
from datetime import datetime

from cryptoconditions import Ed25519Fulfillment, ThresholdSha256Fulfillment
from cryptoconditions.fulfillment import Fulfillment

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


# TODO: Consider remove the operation (if there are no inputs CREATE else TRANSFER)
def create_tx(current_owners, new_owners, inputs, operation, payload=None):
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
        current_owners (list): base58 encoded public key of the current owners of the asset.
        new_owners (list): base58 encoded public key of the new owners of the digital asset.
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
            "version": "transaction version number",
            "transaction": {
                "fulfillments": [
                        {
                            "current_owners": ["list of <pub-keys>"],
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
                            "new_owners": ["list of <pub-keys>"],
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
    current_owners = current_owners if isinstance(current_owners, list) else [current_owners]
    new_owners = new_owners if isinstance(new_owners, list) else [new_owners]
    inputs = inputs if isinstance(inputs, list) else [inputs]

    # validate arguments (owners and inputs should be lists)
    if not isinstance(current_owners, list):
        current_owners = [current_owners]
    if not isinstance(new_owners, list):
        new_owners = [new_owners]
    if not isinstance(inputs, list):
        inputs = [inputs]

    # handle payload
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

    # handle inputs
    fulfillments = []

    # transfer
    if inputs:
        for fid, inp in enumerate(inputs):
            fulfillments.append({
                'current_owners': current_owners,
                'input': inp,
                'fulfillment': None,
                'fid': fid
            })
    # create
    else:
        fulfillments.append({
            'current_owners': current_owners,
            'input': None,
            'fulfillment': None,
            'fid': 0
        })

    # handle outputs
    conditions = []
    for fulfillment in fulfillments:
        if len(new_owners) > 1:
            condition = ThresholdSha256Fulfillment(threshold=len(new_owners))
            for new_owner in new_owners:
                condition.add_subfulfillment(Ed25519Fulfillment(public_key=new_owner))
        elif len(new_owners) == 1:
            condition = Ed25519Fulfillment(public_key=new_owners[0])
        conditions.append({
            'new_owners': new_owners,
            'condition': {
                'details': json.loads(condition.serialize_json()),
                'uri': condition.condition.serialize_uri()
            },
            'cid': fulfillment['fid']
        })

    tx = {
        'fulfillments': fulfillments,
        'conditions': conditions,
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
        'version': 1,
        'transaction': tx
    }

    return transaction


# TODO: Change sign_tx to populate the fulfillments
def sign_tx(transaction, sks):
    """Sign a transaction

    A transaction signed with the `current_owner` corresponding private key.

    Args:
        transaction (dict): transaction to sign.
        sk (base58 str): base58 encoded private key to create a signature of the transaction.

    Returns:
        dict: transaction with the `fulfillment` fields populated.

    """
    # validate sk
    if not isinstance(sks, list):
        sks = [sks]

    # create a mapping between sk and vk so that we can match the private key to the current_owners
    key_pairs = {}
    for sk in sks:
        signing_key = crypto.SigningKey(sk)
        vk = signing_key.get_verifying_key().to_ascii().decode()
        key_pairs[vk] = signing_key

    tx = copy.deepcopy(transaction)

    for fulfillment in tx['transaction']['fulfillments']:
        fulfillment_message = get_fulfillment_message(transaction, fulfillment)
        parsed_fulfillment = Fulfillment.from_json(fulfillment_message['condition']['condition']['details'])

        # single current owner
        if isinstance(parsed_fulfillment, Ed25519Fulfillment):
            current_owner = fulfillment['current_owners'][0]
            try:
                parsed_fulfillment.sign(serialize(fulfillment_message), key_pairs[current_owner])
            except KeyError:
                raise exceptions.KeypairMismatchException('Public key {} is not a pair to any of the private keys'
                                                          .format(current_owner))
        # multiple current owners
        elif isinstance(parsed_fulfillment, ThresholdSha256Fulfillment):
            # replace the fulfillments with the signed fulfillments
            parsed_fulfillment.subconditions = []
            for current_owner in fulfillment['current_owners']:
                subfulfillment = get_subcondition_from_vk(fulfillment_message['condition'], current_owner)
                try:
                    subfulfillment.sign(serialize(fulfillment_message), key_pairs[current_owner])
                except KeyError:
                    raise exceptions.KeypairMismatchException('Public key {} is not a pair to any of the private keys'
                                                              .format(current_owner))
                parsed_fulfillment.add_subfulfillment(subfulfillment)

        signed_fulfillment = parsed_fulfillment.serialize_uri()
        fulfillment.update({'fulfillment': signed_fulfillment})

    return tx


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
    # TODO: The name should change. This will be the validation of the fulfillments
    """Verify the signature of a transaction

    A valid transaction should have been signed `current_owner` corresponding private key.

    Args:
        signed_transaction (dict): a transaction with the `signature` included.

    Returns:
        bool: True if the signature is correct, False otherwise.
    """

    for fulfillment in signed_transaction['transaction']['fulfillments']:
        fulfillment_message = get_fulfillment_message(signed_transaction, fulfillment)
        # verify the fulfillment (for now lets assume there is only one owner)
        try:
            parsed_fulfillment = Fulfillment.from_uri(fulfillment['fulfillment'])
        except Exception:
            return False
        is_valid = parsed_fulfillment.validate(serialize(fulfillment_message))

        # if not a `CREATE` transaction
        if fulfillment['input']:
            is_valid &= parsed_fulfillment.condition.serialize_uri() == \
                fulfillment_message['condition']['condition']['uri']
        if not is_valid:
            return False

    return True


def get_fulfillment_message(transaction, fulfillment):
    b = bigchaindb.Bigchain()

    common_data = {
        'operation': transaction['transaction']['operation'],
        'timestamp': transaction['transaction']['timestamp'],
        'data': transaction['transaction']['data'],
        'version': transaction['version'],
        'id': transaction['id']
    }

    fulfillment_message = common_data.copy()
    fulfillment_message.update({
        'input': fulfillment['input'],
        'condition': None,
    })

    # if `TRANSFER` transaction
    if fulfillment['input']:
        # get previous condition
        previous_tx = b.get_transaction(fulfillment['input']['txid'])
        conditions = sorted(previous_tx['transaction']['conditions'], key=lambda d: d['cid'])
        fulfillment_message['condition'] = conditions[fulfillment['input']['cid']]
    # if `CREATE` transaction
    # there is no previous transaction so we need to create one on the fly
    else:
        current_owner = transaction['transaction']['fulfillments'][0]['current_owners'][0]
        condition = json.loads(Ed25519Fulfillment(public_key=current_owner).serialize_json())
        fulfillment_message['condition'] = {'condition': {'details': condition}}
    return fulfillment_message


def get_subcondition_from_vk(condition, vk):
    threshold_fulfillment = Fulfillment.from_json(condition['condition']['details'])
    for subcondition in threshold_fulfillment.subconditions:
        if subcondition['body'].public_key.to_ascii().decode() == vk:
            return subcondition['body']


def transform_create(tx):
    """Change the owner and signature for a ``CREATE`` transaction created by a node"""

    # XXX: the next instruction opens a new connection to the DB, consider using a singleton or a global
    #      if you need a Bigchain instance.
    b = bigchaindb.Bigchain()
    transaction = tx['transaction']
    payload = None
    if transaction['data'] and 'payload' in transaction['data']:
        payload = transaction['data']['payload']
    new_tx = create_tx(b.me, transaction['fulfillments'][0]['current_owners'], None, 'CREATE', payload=payload)
    return new_tx

