from bigchaindb.common.crypto import hash_data, VerifyingKey, SigningKey
from bigchaindb.common.exceptions import (InvalidHash, InvalidSignature,
                                          OperationError, DoubleSpend,
                                          TransactionDoesNotExist,
                                          FulfillmentNotInValidBlock,
                                          AssetIdMismatch)
from bigchaindb.common.transaction import Transaction, Asset
from bigchaindb.common.util import gen_timestamp, serialize


class Asset(Asset):
    @staticmethod
    def get_asset_id(transactions):
        """Get the asset id from a list of transaction ids.

        This is useful when we want to check if the multiple inputs of a transaction
        are related to the same asset id.

        Args:
            transactions (list): list of transaction usually inputs that should have a matching asset_id

        Returns:
            str: uuid of the asset.

        Raises:
            AssetIdMismatch: If the inputs are related to different assets.
        """

        if not isinstance(transactions, list):
            transactions = [transactions]

        # create a set of asset_ids
        asset_ids = {tx.asset.data_id for tx in transactions}

        # check that all the transasctions have the same asset_id
        if len(asset_ids) > 1:
            raise AssetIdMismatch("All inputs of a transaction need to have the same asset id.")
        return asset_ids.pop()


class Transaction(Transaction):
    def validate(self, bigchain):
        """Validate a transaction.

        Args:
            bigchain (Bigchain): an instantiated bigchaindb.Bigchain object.

        Returns:
            The transaction (Transaction) if the transaction is valid else it
            raises an exception describing the reason why the transaction is
            invalid.

        Raises:
            OperationError: if the transaction operation is not supported
            TransactionDoesNotExist: if the input of the transaction is not
                                     found
            TransactionOwnerError: if the new transaction is using an input it
                                   doesn't own
            DoubleSpend: if the transaction is a double spend
            InvalidHash: if the hash of the transaction is wrong
            InvalidSignature: if the signature of the transaction is wrong
        """
        if len(self.fulfillments) == 0:
            raise ValueError('Transaction contains no fulfillments')

        input_conditions = []
        inputs_defined = all([ffill.tx_input for ffill in self.fulfillments])

        if self.operation in (Transaction.CREATE, Transaction.GENESIS):
            # validate inputs
            if inputs_defined:
                raise ValueError('A CREATE operation has no inputs')
            # validate asset
            self.asset._validate_asset()
        elif self.operation == Transaction.TRANSFER:
            if not inputs_defined:
                raise ValueError('Only `CREATE` transactions can have null '
                                 'inputs')
            # check inputs
            # store the inputs so that we can check if the asset ids match
            input_txs = []
            for ffill in self.fulfillments:
                input_txid = ffill.tx_input.txid
                input_cid = ffill.tx_input.cid
                input_tx, status = bigchain.\
                    get_transaction(input_txid, include_status=True)

                if input_tx is None:
                    raise TransactionDoesNotExist("input `{}` doesn't exist"
                                                  .format(input_txid))

                if status != bigchain.TX_VALID:
                    raise FulfillmentNotInValidBlock(
                        'input `{}` does not exist in a valid block'.format(
                            input_txid))

                spent = bigchain.get_spent(input_txid, ffill.tx_input.cid)
                if spent and spent.id != self.id:
                    raise DoubleSpend('input `{}` was already spent'
                                      .format(input_txid))

                input_conditions.append(input_tx.conditions[input_cid])
                input_txs.append(input_tx)

            # validate asset id
            asset_id = Asset.get_asset_id(input_txs)
            if asset_id != self.asset.data_id:
                raise AssetIdMismatch('The asset id of the input does not match the asset id of the transaction')
        else:
            allowed_operations = ', '.join(Transaction.ALLOWED_OPERATIONS)
            raise TypeError('`operation`: `{}` must be either {}.'
                            .format(self.operation, allowed_operations))

        if not self.fulfillments_valid(input_conditions):
            raise InvalidSignature()
        else:
            return self


class Block(object):
    def __init__(self, transactions=None, node_pubkey=None, timestamp=None,
                 voters=None, signature=None):
        if transactions is not None and not isinstance(transactions, list):
            raise TypeError('`transactions` must be a list instance or None')
        else:
            self.transactions = transactions or []

        if voters is not None and not isinstance(voters, list):
            raise TypeError('`voters` must be a list instance or None')
        else:
            self.voters = voters or []

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

    def validate(self, bigchain):
        """Validate a block.

        Args:
            bigchain (Bigchain): an instantiated bigchaindb.Bigchain object.

        Returns:
            block (Block): The block as a `Block` object if it is valid.
                           Else it raises an appropriate exception describing
                           the reason of invalidity.

        Raises:
            OperationError: if a non-federation node signed the block.
        """

        # First, make sure this node hasn't already voted on this block
        if bigchain.has_previous_vote(self.id, self.voters):
            return self

        # Check if the block was created by a federation node
        possible_voters = (bigchain.nodes_except_me + [bigchain.me])
        if self.node_pubkey not in possible_voters:
            raise OperationError('Only federation nodes can create blocks')

        if not self.is_signature_valid():
            raise InvalidSignature('Block signature invalid')

        # Finally: Tentative assumption that every blockchain will want to
        # validate all transactions in each block
        for tx in self.transactions:
            # NOTE: If a transaction is not valid, `is_valid` will throw an
            #       an exception and block validation will be canceled.
            bigchain.validate_transaction(tx)

        return self

    def sign(self, signing_key):
        block_body = self.to_dict()
        block_serialized = serialize(block_body['block'])
        signing_key = SigningKey(signing_key)
        self.signature = signing_key.sign(block_serialized.encode()).decode()
        return self

    def is_signature_valid(self):
        block = self.to_dict()['block']
        # cc only accepts bytesting messages 
        block_serialized = serialize(block).encode()
        verifying_key = VerifyingKey(block['node_pubkey'])
        try:
            # NOTE: CC throws a `ValueError` on some wrong signatures
            #       https://github.com/bigchaindb/cryptoconditions/issues/27
            return verifying_key.verify(block_serialized, self.signature)
        except (ValueError, AttributeError):
            return False

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
            # NOTE: CC throws a `ValueError` on some wrong signatures
            #       https://github.com/bigchaindb/cryptoconditions/issues/27
            try:
                signature_valid = verifying_key\
                        .verify(block_serialized.encode(), signature)
            except ValueError:
                signature_valid = False
            if signature_valid is False:
                raise InvalidSignature('Invalid block signature')

        transactions = [Transaction.from_dict(tx) for tx
                        in block['transactions']]

        return cls(transactions, block['node_pubkey'],
                   block['timestamp'], block['voters'], signature)

    @property
    def id(self):
        return self.to_dict()['id']

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

    def to_str(self):
        return serialize(self.to_dict())
