from bigchaindb_common.crypto import hash_data, VerifyingKey, SigningKey
from bigchaindb_common.exceptions import (InvalidHash, InvalidSignature,
                                          OperationError)
from bigchaindb_common.transaction import Transaction
from bigchaindb_common.util import gen_timestamp, serialize


class Block(object):
    def __init__(self, transactions=None, node_pubkey=None, timestamp=None,
                 voters=None, signature=None):
        if transactions is not None and not isinstance(transactions, list):
            raise TypeError('`transactions` must be a list instance or None')
        elif transactions is None:
            self.transactions = []
        else:
            self.transactions = transactions

        if voters is not None and not isinstance(voters, list):
            raise TypeError('`voters` must be a list instance or None')
        elif transactions is None:
            self.voters = []
        else:
            self.voters = voters

        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = gen_timestamp()

        self.node_pubkey = node_pubkey
        self.signature = signature

    def __eq__(self, other):
        try:
            other = other.to_dict()
        except AttributeError:
            return False
        return self.to_dict() == other

    def sign(self, private_key):
        block_body = self.to_dict()
        block_serialized = serialize(block_body['block'])
        private_key = SigningKey(private_key)
        self.signature = private_key.sign(block_serialized)
        return self

    @classmethod
    def from_dict(cls, block_body):
        block = block_body['block']
        block_serialized = serialize(block)
        block_id = hash_data(block_serialized)
        verifying_key = VerifyingKey(block['node_pubkey'])

        try:
            signature = block_body['signature']
        except KeyError:
            signature = None

        if block_id != block_body['id']:
            raise InvalidHash()

        if signature is not None:
            # TODO FOR CC: `verify` should accept an arbitrary string and then
            #              return `False` or `True`. Shouldn't throw value err.
            try:
                signature_valid = verifying_key.verify(block_serialized,
                                                       signature)
            except ValueError:
                signature_valid = False
            if signature_valid is False:
                raise InvalidSignature('Invalid block signature')

        transactions = [Transaction.from_dict(tx) for tx
                        in block['transactions']]

        return cls(transactions, block['node_pubkey'],
                   block['timestamp'], block['voters'], signature)

    def to_dict(self):
        if len(self.transactions) == 0:
            raise OperationError('Empty block creation is not allowed')

        block = {
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'node_pubkey': self.node_pubkey,
            'voters': self.voters,
        }
        block_serialized = serialize(block)
        block_id = hash_data(block_serialized)

        return {
            'id': block_id,
            'block': block,
            'signature': self.signature,
        }
