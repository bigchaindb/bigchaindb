from copy import deepcopy

from bigchaindb.common.crypto import hash_data, PublicKey, PrivateKey
from bigchaindb.common.exceptions import (InvalidHash, InvalidSignature,
                                          DoubleSpend, InputDoesNotExist,
                                          TransactionNotInValidBlock,
                                          AssetIdMismatch, AmountError,
                                          SybilError,
                                          DuplicateTransaction)
from bigchaindb.common.transaction import Transaction
from bigchaindb.common.utils import (gen_timestamp, serialize,
                                     validate_txn_obj, validate_key)
from bigchaindb.common.schema import validate_transaction_schema
from bigchaindb.backend.schema import validate_language_key


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
        validate_txn_obj('asset', tx_body['asset'], 'data', validate_key)
        validate_txn_obj('metadata', tx_body, 'metadata', validate_key)
        validate_language_key(tx_body['asset'], 'data')
        return super().from_dict(tx_body)

    @classmethod
    def from_db(cls, bigchain, tx_dict):
        """
        Helper method that reconstructs a transaction dict that was returned
        from the database. It checks what asset_id to retrieve, retrieves the
        asset from the asset table and reconstructs the transaction.

        Args:
            bigchain (:class:`~bigchaindb.Bigchain`): An instance of Bigchain
                used to perform database queries.
            tx_dict (:obj:`dict`): The transaction dict as returned from the
                database.

        Returns:
            :class:`~Transaction`

        """
        if tx_dict['operation'] in [Transaction.CREATE, Transaction.GENESIS]:
            # TODO: Maybe replace this call to a call to get_asset_by_id
            asset = list(bigchain.get_assets([tx_dict['id']]))[0]
            del asset['id']
            tx_dict.update({'asset': asset})

        return cls.from_dict(tx_dict)


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
    def from_dict(cls, block_body, tx_construct=Transaction.from_dict):
        """Transform a Python dictionary to a Block object.

        Args:
            block_body (dict): A block dictionary to be transformed.
            tx_construct (functions): Function to instantiate Transaction instance

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

        transactions = [tx_construct(tx) for tx in block['transactions']]

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

    @classmethod
    def from_db(cls, bigchain, block_dict, from_dict_kwargs=None):
        """
        Helper method that reconstructs a block_dict that was returned from
        the database. It checks what asset_ids to retrieve, retrieves the
        assets from the assets table and reconstructs the block.

        Args:
            bigchain (:class:`~bigchaindb.Bigchain`): An instance of Bigchain
                used to perform database queries.
            block_dict(:obj:`dict`): The block dict as returned from the
                database.
            from_dict_kwargs (:obj:`dict`): additional kwargs to pass to from_dict

        Returns:
            :class:`~Block`

        """
        asset_ids = cls.get_asset_ids(block_dict)
        assets = bigchain.get_assets(asset_ids)
        block_dict = cls.couple_assets(block_dict, assets)
        kwargs = from_dict_kwargs or {}
        return cls.from_dict(block_dict, **kwargs)

    def decouple_assets(self):
        """
        Extracts the assets from the ``CREATE`` transactions in the block.

        Returns:
            tuple: (assets, block) with the assets being a list of dicts and
            the block being the dict of the block with no assets in the CREATE
            transactions.
        """
        block_dict = deepcopy(self.to_dict())
        assets = []
        for transaction in block_dict['block']['transactions']:
            if transaction['operation'] in [Transaction.CREATE,
                                            Transaction.GENESIS]:
                asset = transaction.pop('asset')
                asset.update({'id': transaction['id']})
                assets.append(asset)

        return (assets, block_dict)

    @staticmethod
    def couple_assets(block_dict, assets):
        """
        Given a block_dict with no assets (as returned from a database call)
        and a list of assets, reconstruct the original block by putting the
        assets back into the ``CREATE`` transactions in the block.

        Args:
            block_dict (:obj:`dict`): The block dict as returned from a
                database call.
            assets (:obj:`list` of :obj:`dict`): A list of assets returned from
                a database call.

        Returns:
            dict: The dict of the reconstructed block.
        """
        # create a dict with {'<txid>': asset}
        assets = {asset.pop('id'): asset for asset in assets}
        # add the assets to the block transactions
        for transaction in block_dict['block']['transactions']:
            if transaction['operation'] in [Transaction.CREATE,
                                            Transaction.GENESIS]:
                transaction.update({'asset': assets.get(transaction['id'])})
        return block_dict

    @staticmethod
    def get_asset_ids(block_dict):
        """
        Given a block_dict return all the asset_ids for that block (the txid
        of CREATE transactions). Useful to know which assets to retrieve
        from the database to reconstruct the block.

        Args:
            block_dict (:obj:`dict`): The block dict as returned from a
                database call.

        Returns:
            list: The list of asset_ids in the block.

        """
        asset_ids = []
        for transaction in block_dict['block']['transactions']:
            if transaction['operation'] in [Transaction.CREATE,
                                            Transaction.GENESIS]:
                asset_ids.append(transaction['id'])

        return asset_ids

    def to_str(self):
        return serialize(self.to_dict())


class FastTransaction:
    """
    A minimal wrapper around a transaction dictionary. This is useful for
    when validation is not required but a routine expects something that looks
    like a transaction, for example during block creation.

    Note: immutability could also be provided
    """
    def __init__(self, tx_dict):
        self.data = tx_dict

    @property
    def id(self):
        return self.data['id']

    def to_dict(self):
        return self.data
