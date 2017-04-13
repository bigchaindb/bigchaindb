from bigchaindb.common.crypto import hash_data, PublicKey, PrivateKey
from bigchaindb.common.exceptions import (InvalidHash, InvalidSignature,
                                          DoubleSpend, InputDoesNotExist,
                                          TransactionNotInValidBlock,
                                          AssetIdMismatch, AmountError,
                                          SybilError,
                                          DuplicateTransaction)
from bigchaindb.common.transaction import Transaction
from bigchaindb.common.utils import gen_timestamp, serialize
from bigchaindb.common.schema import validate_transaction_schema


class Transaction(Transaction):
    def validate(self, bigchain):
        """Validate transaction spend

        Args:
            bigchain (Bigchain): an instantiated bigchaindb.Bigchain object.

        Returns:
            The transaction (Transaction) if the transaction is valid else it
            raises an exception describing the reason why the transaction is
            invalid.

        Raises:
            ValidationError: If the transaction is invalid
        """
        input_conditions = []

        if self.operation == Transaction.TRANSFER:
            # store the inputs so that we can check if the asset ids match
            input_txs = []
            for input_ in self.inputs:
                input_txid = input_.fulfills.txid
                input_tx, status = bigchain.\
                    get_transaction(input_txid, include_status=True)

                if input_tx is None:
                    raise InputDoesNotExist("input `{}` doesn't exist"
                                            .format(input_txid))

                if status != bigchain.TX_VALID:
                    raise TransactionNotInValidBlock(
                        'input `{}` does not exist in a valid block'.format(
                            input_txid))

                spent = bigchain.get_spent(input_txid, input_.fulfills.output)
                if spent and spent.id != self.id:
                    raise DoubleSpend('input `{}` was already spent'
                                      .format(input_txid))

                output = input_tx.outputs[input_.fulfills.output]
                input_conditions.append(output)
                input_txs.append(input_tx)

            # Validate that all inputs are distinct
            links = [i.fulfills.to_uri() for i in self.inputs]
            if len(links) != len(set(links)):
                raise DoubleSpend('tx "{}" spends inputs twice'.format(self.id))

            # validate asset id
            asset_id = Transaction.get_asset_id(input_txs)
            if asset_id != self.asset['id']:
                raise AssetIdMismatch(('The asset id of the input does not'
                                       ' match the asset id of the'
                                       ' transaction'))

            input_amount = sum([input_condition.amount for input_condition in input_conditions])
            output_amount = sum([output_condition.amount for output_condition in self.outputs])

            if output_amount != input_amount:
                raise AmountError(('The amount used in the inputs `{}`'
                                   ' needs to be same as the amount used'
                                   ' in the outputs `{}`')
                                  .format(input_amount, output_amount))

        if not self.inputs_valid(input_conditions):
            raise InvalidSignature('Transaction signature is invalid.')

        return self

    @classmethod
    def from_dict(cls, tx_body):
        validate_transaction_schema(tx_body)
        return super().from_dict(tx_body)


class Block(object):
    """Bundle a list of Transactions in a Block. Nodes vote on its validity.

    Attributes:
        transaction (:obj:`list` of :class:`~.Transaction`):
            Transactions to be included in the Block.
        node_pubkey (str): The public key of the node creating the
            Block.
        timestamp (str): The Unix time a Block was created.
        voters (:obj:`list` of :obj:`str`): A list of a federation
            nodes' public keys supposed to vote on the Block.
        signature (str): A cryptographic signature ensuring the
            integrity and validity of the creator of a Block.
    """

    def __init__(self, transactions=None, node_pubkey=None, timestamp=None,
                 voters=None, signature=None):
        """The Block model is mainly used for (de)serialization and integrity
        checking.

        Args:
            transaction (:obj:`list` of :class:`~.Transaction`):
                Transactions to be included in the Block.
            node_pubkey (str): The public key of the node creating the
                Block.
            timestamp (str): The Unix time a Block was created.
            voters (:obj:`list` of :obj:`str`): A list of a federation
                nodes' public keys supposed to vote on the Block.
            signature (str): A cryptographic signature ensuring the
                integrity and validity of the creator of a Block.
        """
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
        """Validate the Block.

        Args:
            bigchain (:class:`~bigchaindb.Bigchain`): An instantiated Bigchain
                object.

        Note:
            The hash of the block (`id`) is validated on the `self.from_dict`
            method. This is because the `from_dict` is the only method in
            which we have the original json payload. The `id` provided by
            this class is a mutable property that is generated on the fly.

        Returns:
            :class:`~.Block`: If valid, return a `Block` object. Else an
            appropriate exception describing the reason of invalidity is
            raised.

        Raises:
            ValidationError: If the block or any transaction in the block does
                             not validate
        """

        self._validate_block(bigchain)
        self._validate_block_transactions(bigchain)

        return self

    def _validate_block(self, bigchain):
        """Validate the Block without validating the transactions.

        Args:
            bigchain (:class:`~bigchaindb.Bigchain`): An instantiated Bigchain
                object.

        Raises:
            ValidationError: If there is a problem with the block
        """
        # Check if the block was created by a federation node
        if self.node_pubkey not in bigchain.federation:
            raise SybilError('Only federation nodes can create blocks')

        # Check that the signature is valid
        if not self.is_signature_valid():
            raise InvalidSignature('Invalid block signature')

        # Check that the block contains no duplicated transactions
        txids = [tx.id for tx in self.transactions]
        if len(txids) != len(set(txids)):
            raise DuplicateTransaction('Block has duplicate transaction')

    def _validate_block_transactions(self, bigchain):
        """Validate Block transactions.

        Args:
            bigchain (Bigchain): an instantiated bigchaindb.Bigchain object.

        Raises:
            ValidationError: If an invalid transaction is found
        """
        for tx in self.transactions:
            # If a transaction is not valid, `validate_transactions` will
            # throw an an exception and block validation will be canceled.
            bigchain.validate_transaction(tx)

    def sign(self, private_key):
        """Create a signature for the Block and overwrite `self.signature`.

        Args:
            private_key (str): A private key corresponding to
                `self.node_pubkey`.

        Returns:
            :class:`~.Block`
        """
        block_body = self.to_dict()
        block_serialized = serialize(block_body['block'])
        private_key = PrivateKey(private_key)
        self.signature = private_key.sign(block_serialized.encode()).decode()
        return self

    def is_signature_valid(self):
        """Check the validity of a Block's signature.

        Returns:
            bool: Stating the validity of the Block's signature.
        """
        block = self.to_dict()['block']
        # cc only accepts bytestring messages
        block_serialized = serialize(block).encode()
        public_key = PublicKey(block['node_pubkey'])
        try:
            # NOTE: CC throws a `ValueError` on some wrong signatures
            #       https://github.com/bigchaindb/cryptoconditions/issues/27
            return public_key.verify(block_serialized, self.signature)
        except (ValueError, AttributeError):
            return False

    @classmethod
    def from_dict(cls, block_body):
        """Transform a Python dictionary to a Block object.

        Args:
            block_body (dict): A block dictionary to be transformed.

        Returns:
            :class:`~Block`

        Raises:
            InvalidHash: If the block's id is not corresponding to its
                data.
        """
        # Validate block id
        block = block_body['block']
        block_serialized = serialize(block)
        block_id = hash_data(block_serialized)

        if block_id != block_body['id']:
            raise InvalidHash()

        transactions = [Transaction.from_dict(tx) for tx
                        in block['transactions']]

        signature = block_body.get('signature')

        return cls(transactions, block['node_pubkey'],
                   block['timestamp'], block['voters'], signature)

    @property
    def id(self):
        return self.to_dict()['id']

    def to_dict(self):
        """Transform the Block to a Python dictionary.

        Returns:
            dict: The Block as a dict.

        Raises:
            ValueError: If the Block doesn't contain any transactions.
        """
        if len(self.transactions) == 0:
            raise ValueError('Empty block creation is not allowed')

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
