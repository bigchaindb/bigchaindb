"""Transaction related models to parse and construct transaction
payloads.

Attributes:
    UnspentOutput (namedtuple): Object holding the information
        representing an unspent output.

"""
from collections import namedtuple
from copy import deepcopy
from functools import reduce

import base58
from cryptoconditions import Fulfillment, ThresholdSha256, Ed25519Sha256
from cryptoconditions.exceptions import (
    ParsingError, ASN1DecodeError, ASN1EncodeError, UnsupportedTypeError)
from sha3 import sha3_256

from bigchaindb.common.crypto import PrivateKey, hash_data
from bigchaindb.common.exceptions import (KeypairMismatchException,
                                          InvalidHash, InvalidSignature,
                                          AmountError, AssetIdMismatch,
                                          ThresholdTooDeep)
from bigchaindb.common.utils import serialize


UnspentOutput = namedtuple(
    'UnspentOutput', (
        # TODO 'utxo_hash': sha3_256(f'{txid}{output_index}'.encode())
        # 'utxo_hash',   # noqa
        'transaction_id',
        'output_index',
        'amount',
        'asset_id',
        'condition_uri',
    )
)


class Input(object):
    """A Input is used to spend assets locked by an Output.

    Wraps around a Crypto-condition Fulfillment.

        Attributes:
            fulfillment (:class:`cryptoconditions.Fulfillment`): A Fulfillment
                to be signed with a private key.
            owners_before (:obj:`list` of :obj:`str`): A list of owners after a
                Transaction was confirmed.
            fulfills (:class:`~bigchaindb.common.transaction. TransactionLink`,
                optional): A link representing the input of a `TRANSFER`
                Transaction.
    """

    def __init__(self, fulfillment, owners_before, fulfills=None):
        """Create an instance of an :class:`~.Input`.

            Args:
                fulfillment (:class:`cryptoconditions.Fulfillment`): A
                    Fulfillment to be signed with a private key.
                owners_before (:obj:`list` of :obj:`str`): A list of owners
                    after a Transaction was confirmed.
                fulfills (:class:`~bigchaindb.common.transaction.
                    TransactionLink`, optional): A link representing the input
                    of a `TRANSFER` Transaction.
        """
        if fulfills is not None and not isinstance(fulfills, TransactionLink):
            raise TypeError('`fulfills` must be a TransactionLink instance')
        if not isinstance(owners_before, list):
            raise TypeError('`owners_after` must be a list instance')

        self.fulfillment = fulfillment
        self.fulfills = fulfills
        self.owners_before = owners_before

    def __eq__(self, other):
        # TODO: If `other !== Fulfillment` return `False`
        return self.to_dict() == other.to_dict()

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Note:
                If an Input hasn't been signed yet, this method returns a
                dictionary representation.

            Returns:
                dict: The Input as an alternative serialization format.
        """
        try:
            fulfillment = self.fulfillment.serialize_uri()
        except (TypeError, AttributeError, ASN1EncodeError):
            fulfillment = _fulfillment_to_details(self.fulfillment)

        try:
            # NOTE: `self.fulfills` can be `None` and that's fine
            fulfills = self.fulfills.to_dict()
        except AttributeError:
            fulfills = None

        input_ = {
            'owners_before': self.owners_before,
            'fulfills': fulfills,
            'fulfillment': fulfillment,
        }
        return input_

    @classmethod
    def generate(cls, public_keys):
        # TODO: write docstring
        # The amount here does not really matter. It is only use on the
        # output data model but here we only care about the fulfillment
        output = Output.generate(public_keys, 1)
        return cls(output.fulfillment, public_keys)

    @classmethod
    def from_dict(cls, data):
        """Transforms a Python dictionary to an Input object.

            Note:
                Optionally, this method can also serialize a Cryptoconditions-
                Fulfillment that is not yet signed.

            Args:
                data (dict): The Input to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.Input`

            Raises:
                InvalidSignature: If an Input's URI couldn't be parsed.
        """
        fulfillment = data['fulfillment']
        if not isinstance(fulfillment, (Fulfillment, type(None))):
            try:
                fulfillment = Fulfillment.from_uri(data['fulfillment'])
            except ASN1DecodeError:
                # TODO Remove as it is legacy code, and simply fall back on
                # ASN1DecodeError
                raise InvalidSignature("Fulfillment URI couldn't been parsed")
            except TypeError:
                # NOTE: See comment about this special case in
                #       `Input.to_dict`
                fulfillment = _fulfillment_from_details(data['fulfillment'])
        fulfills = TransactionLink.from_dict(data['fulfills'])
        return cls(fulfillment, data['owners_before'], fulfills)


def _fulfillment_to_details(fulfillment):
    """Encode a fulfillment as a details dictionary

    Args:
        fulfillment: Crypto-conditions Fulfillment object
    """

    if fulfillment.type_name == 'ed25519-sha-256':
        return {
            'type': 'ed25519-sha-256',
            'public_key': base58.b58encode(fulfillment.public_key),
        }

    if fulfillment.type_name == 'threshold-sha-256':
        subconditions = [
            _fulfillment_to_details(cond['body'])
            for cond in fulfillment.subconditions
        ]
        return {
            'type': 'threshold-sha-256',
            'threshold': fulfillment.threshold,
            'subconditions': subconditions,
        }

    raise UnsupportedTypeError(fulfillment.type_name)


def _fulfillment_from_details(data, _depth=0):
    """Load a fulfillment for a signing spec dictionary

    Args:
        data: tx.output[].condition.details dictionary
    """
    if _depth == 100:
        raise ThresholdTooDeep()

    if data['type'] == 'ed25519-sha-256':
        public_key = base58.b58decode(data['public_key'])
        return Ed25519Sha256(public_key=public_key)

    if data['type'] == 'threshold-sha-256':
        threshold = ThresholdSha256(data['threshold'])
        for cond in data['subconditions']:
            cond = _fulfillment_from_details(cond, _depth+1)
            threshold.add_subfulfillment(cond)
        return threshold

    raise UnsupportedTypeError(data.get('type'))


class TransactionLink(object):
    """An object for unidirectional linking to a Transaction's Output.

        Attributes:
            txid (str, optional): A Transaction to link to.
            output (int, optional): An output's index in a Transaction with id
            `txid`.
    """

    def __init__(self, txid=None, output=None):
        """Create an instance of a :class:`~.TransactionLink`.

            Note:
                In an IPLD implementation, this class is not necessary anymore,
                as an IPLD link can simply point to an object, as well as an
                objects properties. So instead of having a (de)serializable
                class, we can have a simple IPLD link of the form:
                `/<tx_id>/transaction/outputs/<output>/`.

            Args:
                txid (str, optional): A Transaction to link to.
                output (int, optional): An Outputs's index in a Transaction with
                    id `txid`.
        """
        self.txid = txid
        self.output = output

    def __bool__(self):
        return self.txid is not None and self.output is not None

    def __eq__(self, other):
        # TODO: If `other !== TransactionLink` return `False`
        return self.to_dict() == other.to_dict()

    def __hash__(self):
        return hash((self.txid, self.output))

    @classmethod
    def from_dict(cls, link):
        """Transforms a Python dictionary to a TransactionLink object.

            Args:
                link (dict): The link to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.TransactionLink`
        """
        try:
            return cls(link['transaction_id'], link['output_index'])
        except TypeError:
            return cls()

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Returns:
                (dict|None): The link as an alternative serialization format.
        """
        if self.txid is None and self.output is None:
            return None
        else:
            return {
                'transaction_id': self.txid,
                'output_index': self.output,
            }

    def to_uri(self, path=''):
        if self.txid is None and self.output is None:
            return None
        return '{}/transactions/{}/outputs/{}'.format(path, self.txid,
                                                      self.output)


class Output(object):
    """An Output is used to lock an asset.

    Wraps around a Crypto-condition Condition.

        Attributes:
            fulfillment (:class:`cryptoconditions.Fulfillment`): A Fulfillment
                to extract a Condition from.
            public_keys (:obj:`list` of :obj:`str`, optional): A list of
                owners before a Transaction was confirmed.
    """

    MAX_AMOUNT = 9 * 10 ** 18

    def __init__(self, fulfillment, public_keys=None, amount=1):
        """Create an instance of a :class:`~.Output`.

            Args:
                fulfillment (:class:`cryptoconditions.Fulfillment`): A
                    Fulfillment to extract a Condition from.
                public_keys (:obj:`list` of :obj:`str`, optional): A list of
                    owners before a Transaction was confirmed.
                amount (int): The amount of Assets to be locked with this
                    Output.

            Raises:
                TypeError: if `public_keys` is not instance of `list`.
        """
        if not isinstance(public_keys, list) and public_keys is not None:
            raise TypeError('`public_keys` must be a list instance or None')
        if not isinstance(amount, int):
            raise TypeError('`amount` must be an int')
        if amount < 1:
            raise AmountError('`amount` must be greater than 0')
        if amount > self.MAX_AMOUNT:
            raise AmountError('`amount` must be <= %s' % self.MAX_AMOUNT)

        self.fulfillment = fulfillment
        self.amount = amount
        self.public_keys = public_keys

    def __eq__(self, other):
        # TODO: If `other !== Condition` return `False`
        return self.to_dict() == other.to_dict()

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Note:
                A dictionary serialization of the Input the Output was
                derived from is always provided.

            Returns:
                dict: The Output as an alternative serialization format.
        """
        # TODO FOR CC: It must be able to recognize a hashlock condition
        #              and fulfillment!
        condition = {}
        try:
            condition['details'] = _fulfillment_to_details(self.fulfillment)
        except AttributeError:
            pass

        try:
            condition['uri'] = self.fulfillment.condition_uri
        except AttributeError:
            condition['uri'] = self.fulfillment

        output = {
            'public_keys': self.public_keys,
            'condition': condition,
            'amount': str(self.amount),
        }
        return output

    @classmethod
    def generate(cls, public_keys, amount):
        """Generates a Output from a specifically formed tuple or list.

            Note:
                If a ThresholdCondition has to be generated where the threshold
                is always the number of subconditions it is split between, a
                list of the following structure is sufficient:

                [(address|condition)*, [(address|condition)*, ...], ...]

            Args:
                public_keys (:obj:`list` of :obj:`str`): The public key of
                    the users that should be able to fulfill the Condition
                    that is being created.
                amount (:obj:`int`): The amount locked by the Output.

            Returns:
                An Output that can be used in a Transaction.

            Raises:
                TypeError: If `public_keys` is not an instance of `list`.
                ValueError: If `public_keys` is an empty list.
        """
        threshold = len(public_keys)
        if not isinstance(amount, int):
            raise TypeError('`amount` must be a int')
        if amount < 1:
            raise AmountError('`amount` needs to be greater than zero')
        if not isinstance(public_keys, list):
            raise TypeError('`public_keys` must be an instance of list')
        if len(public_keys) == 0:
            raise ValueError('`public_keys` needs to contain at least one'
                             'owner')
        elif len(public_keys) == 1 and not isinstance(public_keys[0], list):
            if isinstance(public_keys[0], Fulfillment):
                ffill = public_keys[0]
            else:
                ffill = Ed25519Sha256(
                    public_key=base58.b58decode(public_keys[0]))
            return cls(ffill, public_keys, amount=amount)
        else:
            initial_cond = ThresholdSha256(threshold=threshold)
            threshold_cond = reduce(cls._gen_condition, public_keys,
                                    initial_cond)
            return cls(threshold_cond, public_keys, amount=amount)

    @classmethod
    def _gen_condition(cls, initial, new_public_keys):
        """Generates ThresholdSha256 conditions from a list of new owners.

            Note:
                This method is intended only to be used with a reduce function.
                For a description on how to use this method, see
                :meth:`~.Output.generate`.

            Args:
                initial (:class:`cryptoconditions.ThresholdSha256`):
                    A Condition representing the overall root.
                new_public_keys (:obj:`list` of :obj:`str`|str): A list of new
                    owners or a single new owner.

            Returns:
                :class:`cryptoconditions.ThresholdSha256`:
        """
        try:
            threshold = len(new_public_keys)
        except TypeError:
            threshold = None

        if isinstance(new_public_keys, list) and len(new_public_keys) > 1:
            ffill = ThresholdSha256(threshold=threshold)
            reduce(cls._gen_condition, new_public_keys, ffill)
        elif isinstance(new_public_keys, list) and len(new_public_keys) <= 1:
            raise ValueError('Sublist cannot contain single owner')
        else:
            try:
                new_public_keys = new_public_keys.pop()
            except AttributeError:
                pass
            # NOTE: Instead of submitting base58 encoded addresses, a user
            #       of this class can also submit fully instantiated
            #       Cryptoconditions. In the case of casting
            #       `new_public_keys` to a Ed25519Fulfillment with the
            #       result of a `TypeError`, we're assuming that
            #       `new_public_keys` is a Cryptocondition then.
            if isinstance(new_public_keys, Fulfillment):
                ffill = new_public_keys
            else:
                ffill = Ed25519Sha256(
                    public_key=base58.b58decode(new_public_keys))
        initial.add_subfulfillment(ffill)
        return initial

    @classmethod
    def from_dict(cls, data):
        """Transforms a Python dictionary to an Output object.

            Note:
                To pass a serialization cycle multiple times, a
                Cryptoconditions Fulfillment needs to be present in the
                passed-in dictionary, as Condition URIs are not serializable
                anymore.

            Args:
                data (dict): The dict to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.Output`
        """
        try:
            fulfillment = _fulfillment_from_details(data['condition']['details'])
        except KeyError:
            # NOTE: Hashlock condition case
            fulfillment = data['condition']['uri']
        try:
            amount = int(data['amount'])
        except ValueError:
            raise AmountError('Invalid amount: %s' % data['amount'])
        return cls(fulfillment, data['public_keys'], amount)


class Transaction(object):
    """A Transaction is used to create and transfer assets.

        Note:
            For adding Inputs and Outputs, this class provides methods
            to do so.

        Attributes:
            operation (str): Defines the operation of the Transaction.
            inputs (:obj:`list` of :class:`~bigchaindb.common.
                transaction.Input`, optional): Define the assets to
                spend.
            outputs (:obj:`list` of :class:`~bigchaindb.common.
                transaction.Output`, optional): Define the assets to lock.
            asset (dict): Asset payload for this Transaction. ``CREATE``
                Transactions require a dict with a ``data``
                property while ``TRANSFER`` Transactions require a dict with a
                ``id`` property.
            metadata (dict):
                Metadata to be stored along with the Transaction.
            version (string): Defines the version number of a Transaction.
    """

    CREATE = 'CREATE'
    TRANSFER = 'TRANSFER'
    ALLOWED_OPERATIONS = (CREATE, TRANSFER)
    VERSION = '2.0'

    def __init__(self, operation, asset, inputs=None, outputs=None,
                 metadata=None, version=None, hash_id=None):
        """The constructor allows to create a customizable Transaction.

            Note:
                When no `version` is provided, one is being
                generated by this method.

            Args:
                operation (str): Defines the operation of the Transaction.
                asset (dict): Asset payload for this Transaction.
                inputs (:obj:`list` of :class:`~bigchaindb.common.
                    transaction.Input`, optional): Define the assets to
                outputs (:obj:`list` of :class:`~bigchaindb.common.
                    transaction.Output`, optional): Define the assets to
                    lock.
                metadata (dict): Metadata to be stored along with the
                    Transaction.
                version (string): Defines the version number of a Transaction.
                hash_id (string): Hash id of the transaction.
        """
        if operation not in self.ALLOWED_OPERATIONS:
            allowed_ops = ', '.join(self.__class__.ALLOWED_OPERATIONS)
            raise ValueError('`operation` must be one of {}'
                             .format(allowed_ops))

        # Asset payloads for 'CREATE' operations must be None or
        # dicts holding a `data` property. Asset payloads for 'TRANSFER'
        # operations must be dicts holding an `id` property.
        if (operation == Transaction.CREATE and
                asset is not None and not (isinstance(asset, dict) and 'data' in asset)):
            raise TypeError(('`asset` must be None or a dict holding a `data` '
                             " property instance for '{}' Transactions".format(operation)))
        elif (operation == Transaction.TRANSFER and
                not (isinstance(asset, dict) and 'id' in asset)):
            raise TypeError(('`asset` must be a dict holding an `id` property '
                             "for 'TRANSFER' Transactions".format(operation)))

        if outputs and not isinstance(outputs, list):
            raise TypeError('`outputs` must be a list instance or None')

        if inputs and not isinstance(inputs, list):
            raise TypeError('`inputs` must be a list instance or None')

        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError('`metadata` must be a dict or None')

        self.version = version if version is not None else self.VERSION
        self.operation = operation
        self.asset = asset
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.metadata = metadata
        self._id = hash_id

    @property
    def unspent_outputs(self):
        """UnspentOutput: The outputs of this transaction, in a data
        structure containing relevant information for storing them in
        a UTXO set, and performing validation.
        """
        if self.operation == Transaction.CREATE:
            self._asset_id = self._id
        elif self.operation == Transaction.TRANSFER:
            self._asset_id = self.asset['id']
        return (UnspentOutput(
            transaction_id=self._id,
            output_index=output_index,
            amount=output.amount,
            asset_id=self._asset_id,
            condition_uri=output.fulfillment.condition_uri,
        ) for output_index, output in enumerate(self.outputs))

    @property
    def spent_outputs(self):
        """tuple of :obj:`dict`: Inputs of this transaction. Each input
        is represented as a dictionary containing a transaction id and
        output index.
        """
        return (
            input_.fulfills.to_dict()
            for input_ in self.inputs if input_.fulfills
        )

    @property
    def serialized(self):
        return Transaction._to_str(self.to_dict())

    def _hash(self):
        self._id = hash_data(self.serialized)

    @classmethod
    def validate_create(cls, tx_signers, recipients, asset, metadata):
        if not isinstance(tx_signers, list):
            raise TypeError('`tx_signers` must be a list instance')
        if not isinstance(recipients, list):
            raise TypeError('`recipients` must be a list instance')
        if len(tx_signers) == 0:
            raise ValueError('`tx_signers` list cannot be empty')
        if len(recipients) == 0:
            raise ValueError('`recipients` list cannot be empty')
        if not (asset is None or isinstance(asset, dict)):
            raise TypeError('`asset` must be a dict or None')
        if not (metadata is None or isinstance(metadata, dict)):
            raise TypeError('`metadata` must be a dict or None')

        inputs = []
        outputs = []

        # generate_outputs
        for recipient in recipients:
            if not isinstance(recipient, tuple) or len(recipient) != 2:
                raise ValueError(('Each `recipient` in the list must be a'
                                  ' tuple of `([<list of public keys>],'
                                  ' <amount>)`'))
            pub_keys, amount = recipient
            outputs.append(Output.generate(pub_keys, amount))

        # generate inputs
        inputs.append(Input.generate(tx_signers))

        return (inputs, outputs)

    @classmethod
    def create(cls, tx_signers, recipients, metadata=None, asset=None):
        """A simple way to generate a `CREATE` transaction.

            Note:
                This method currently supports the following Cryptoconditions
                use cases:
                    - Ed25519
                    - ThresholdSha256

                Additionally, it provides support for the following BigchainDB
                use cases:
                    - Multiple inputs and outputs.

            Args:
                tx_signers (:obj:`list` of :obj:`str`): A list of keys that
                    represent the signers of the CREATE Transaction.
                recipients (:obj:`list` of :obj:`tuple`): A list of
                    ([keys],amount) that represent the recipients of this
                    Transaction.
                metadata (dict): The metadata to be stored along with the
                    Transaction.
                asset (dict): The metadata associated with the asset that will
                    be created in this Transaction.

            Returns:
                :class:`~bigchaindb.common.transaction.Transaction`
        """

        (inputs, outputs) = cls.validate_create(tx_signers, recipients, asset, metadata)
        return cls(cls.CREATE, {'data': asset}, inputs, outputs, metadata)

    @classmethod
    def transfer(cls, inputs, recipients, asset_id, metadata=None):
        """A simple way to generate a `TRANSFER` transaction.

            Note:
                Different cases for threshold conditions:

                Combining multiple `inputs` with an arbitrary number of
                `recipients` can yield interesting cases for the creation of
                threshold conditions we'd like to support. The following
                notation is proposed:

                1. The index of a `recipient` corresponds to the index of
                   an input:
                   e.g. `transfer([input1], [a])`, means `input1` would now be
                        owned by user `a`.

                2. `recipients` can (almost) get arbitrary deeply nested,
                   creating various complex threshold conditions:
                   e.g. `transfer([inp1, inp2], [[a, [b, c]], d])`, means
                        `a`'s signature would have a 50% weight on `inp1`
                        compared to `b` and `c` that share 25% of the leftover
                        weight respectively. `inp2` is owned completely by `d`.

            Args:
                inputs (:obj:`list` of :class:`~bigchaindb.common.transaction.
                    Input`): Converted `Output`s, intended to
                    be used as inputs in the transfer to generate.
                recipients (:obj:`list` of :obj:`tuple`): A list of
                    ([keys],amount) that represent the recipients of this
                    Transaction.
                asset_id (str): The asset ID of the asset to be transferred in
                    this Transaction.
                metadata (dict): Python dictionary to be stored along with the
                    Transaction.

            Returns:
                :class:`~bigchaindb.common.transaction.Transaction`
        """
        if not isinstance(inputs, list):
            raise TypeError('`inputs` must be a list instance')
        if len(inputs) == 0:
            raise ValueError('`inputs` must contain at least one item')
        if not isinstance(recipients, list):
            raise TypeError('`recipients` must be a list instance')
        if len(recipients) == 0:
            raise ValueError('`recipients` list cannot be empty')

        outputs = []
        for recipient in recipients:
            if not isinstance(recipient, tuple) or len(recipient) != 2:
                raise ValueError(('Each `recipient` in the list must be a'
                                  ' tuple of `([<list of public keys>],'
                                  ' <amount>)`'))
            pub_keys, amount = recipient
            outputs.append(Output.generate(pub_keys, amount))

        if not isinstance(asset_id, str):
            raise TypeError('`asset_id` must be a string')

        inputs = deepcopy(inputs)
        return cls(cls.TRANSFER, {'id': asset_id}, inputs, outputs, metadata)

    def __eq__(self, other):
        try:
            other = other.to_dict()
        except AttributeError:
            return False
        return self.to_dict() == other

    def to_inputs(self, indices=None):
        """Converts a Transaction's outputs to spendable inputs.

            Note:
                Takes the Transaction's outputs and derives inputs
                from that can then be passed into `Transaction.transfer` as
                `inputs`.
                A list of integers can be passed to `indices` that
                defines which outputs should be returned as inputs.
                If no `indices` are passed (empty list or None) all
                outputs of the Transaction are returned.

            Args:
                indices (:obj:`list` of int): Defines which
                    outputs should be returned as inputs.

            Returns:
                :obj:`list` of :class:`~bigchaindb.common.transaction.
                    Input`
        """
        # NOTE: If no indices are passed, we just assume to take all outputs
        #       as inputs.
        indices = indices or range(len(self.outputs))
        return [
            Input(self.outputs[idx].fulfillment,
                  self.outputs[idx].public_keys,
                  TransactionLink(self.id, idx))
            for idx in indices
        ]

    def add_input(self, input_):
        """Adds an input to a Transaction's list of inputs.

            Args:
                input_ (:class:`~bigchaindb.common.transaction.
                    Input`): An Input to be added to the Transaction.
        """
        if not isinstance(input_, Input):
            raise TypeError('`input_` must be a Input instance')
        self.inputs.append(input_)

    def add_output(self, output):
        """Adds an output to a Transaction's list of outputs.

            Args:
                output (:class:`~bigchaindb.common.transaction.
                    Output`): An Output to be added to the
                    Transaction.
        """
        if not isinstance(output, Output):
            raise TypeError('`output` must be an Output instance or None')
        self.outputs.append(output)

    def sign(self, private_keys):
        """Fulfills a previous Transaction's Output by signing Inputs.

            Note:
                This method works only for the following Cryptoconditions
                currently:
                    - Ed25519Fulfillment
                    - ThresholdSha256
                Furthermore, note that all keys required to fully sign the
                Transaction have to be passed to this method. A subset of all
                will cause this method to fail.

            Args:
                private_keys (:obj:`list` of :obj:`str`): A complete list of
                    all private keys needed to sign all Fulfillments of this
                    Transaction.

            Returns:
                :class:`~bigchaindb.common.transaction.Transaction`
        """
        # TODO: Singing should be possible with at least one of all private
        #       keys supplied to this method.
        if private_keys is None or not isinstance(private_keys, list):
            raise TypeError('`private_keys` must be a list instance')

        # NOTE: Generate public keys from private keys and match them in a
        #       dictionary:
        #                   key:     public_key
        #                   value:   private_key
        def gen_public_key(private_key):
            # TODO FOR CC: Adjust interface so that this function becomes
            #              unnecessary

            # cc now provides a single method `encode` to return the key
            # in several different encodings.
            public_key = private_key.get_verifying_key().encode()
            # Returned values from cc are always bytestrings so here we need
            # to decode to convert the bytestring into a python str
            return public_key.decode()

        key_pairs = {gen_public_key(PrivateKey(private_key)):
                     PrivateKey(private_key) for private_key in private_keys}

        tx_dict = self.to_dict()
        tx_dict = Transaction._remove_signatures(tx_dict)
        tx_serialized = Transaction._to_str(tx_dict)
        for i, input_ in enumerate(self.inputs):
            self.inputs[i] = self._sign_input(input_, tx_serialized, key_pairs)

        self._hash()

        return self

    @classmethod
    def _sign_input(cls, input_, message, key_pairs):
        """Signs a single Input.

            Note:
                This method works only for the following Cryptoconditions
                currently:
                    - Ed25519Fulfillment
                    - ThresholdSha256.

            Args:
                input_ (:class:`~bigchaindb.common.transaction.
                    Input`) The Input to be signed.
                message (str): The message to be signed
                key_pairs (dict): The keys to sign the Transaction with.
        """
        if isinstance(input_.fulfillment, Ed25519Sha256):
            return cls._sign_simple_signature_fulfillment(input_, message,
                                                          key_pairs)
        elif isinstance(input_.fulfillment, ThresholdSha256):
            return cls._sign_threshold_signature_fulfillment(input_, message,
                                                             key_pairs)
        else:
            raise ValueError("Fulfillment couldn't be matched to "
                             'Cryptocondition fulfillment type.')

    @classmethod
    def _sign_simple_signature_fulfillment(cls, input_, message, key_pairs):
        """Signs a Ed25519Fulfillment.

            Args:
                input_ (:class:`~bigchaindb.common.transaction.
                    Input`) The input to be signed.
                message (str): The message to be signed
                key_pairs (dict): The keys to sign the Transaction with.
        """
        # NOTE: To eliminate the dangers of accidentally signing a condition by
        #       reference, we remove the reference of input_ here
        #       intentionally. If the user of this class knows how to use it,
        #       this should never happen, but then again, never say never.
        input_ = deepcopy(input_)
        public_key = input_.owners_before[0]
        message = sha3_256(message.encode())
        if input_.fulfills:
            message.update('{}{}'.format(
                input_.fulfills.txid, input_.fulfills.output).encode())

        try:
            # cryptoconditions makes no assumptions of the encoding of the
            # message to sign or verify. It only accepts bytestrings
            input_.fulfillment.sign(
                message.digest(), base58.b58decode(key_pairs[public_key].encode()))
        except KeyError:
            raise KeypairMismatchException('Public key {} is not a pair to '
                                           'any of the private keys'
                                           .format(public_key))
        return input_

    @classmethod
    def _sign_threshold_signature_fulfillment(cls, input_, message, key_pairs):
        """Signs a ThresholdSha256.

            Args:
                input_ (:class:`~bigchaindb.common.transaction.
                    Input`) The Input to be signed.
                message (str): The message to be signed
                key_pairs (dict): The keys to sign the Transaction with.
        """
        input_ = deepcopy(input_)
        message = sha3_256(message.encode())
        if input_.fulfills:
            message.update('{}{}'.format(
                input_.fulfills.txid, input_.fulfills.output).encode())

        for owner_before in set(input_.owners_before):
            # TODO: CC should throw a KeypairMismatchException, instead of
            #       our manual mapping here

            # TODO FOR CC: Naming wise this is not so smart,
            #              `get_subcondition` in fact doesn't return a
            #              condition but a fulfillment

            # TODO FOR CC: `get_subcondition` is singular. One would not
            #              expect to get a list back.
            ccffill = input_.fulfillment
            subffills = ccffill.get_subcondition_from_vk(
                base58.b58decode(owner_before))
            if not subffills:
                raise KeypairMismatchException('Public key {} cannot be found '
                                               'in the fulfillment'
                                               .format(owner_before))
            try:
                private_key = key_pairs[owner_before]
            except KeyError:
                raise KeypairMismatchException('Public key {} is not a pair '
                                               'to any of the private keys'
                                               .format(owner_before))

            # cryptoconditions makes no assumptions of the encoding of the
            # message to sign or verify. It only accepts bytestrings
            for subffill in subffills:
                subffill.sign(
                    message.digest(), base58.b58decode(private_key.encode()))
        return input_

    def inputs_valid(self, outputs=None):
        """Validates the Inputs in the Transaction against given
        Outputs.

            Note:
                Given a `CREATE` Transaction is passed,
                dummy values for Outputs are submitted for validation that
                evaluate parts of the validation-checks to `True`.

            Args:
                outputs (:obj:`list` of :class:`~bigchaindb.common.
                    transaction.Output`): A list of Outputs to check the
                    Inputs against.

            Returns:
                bool: If all Inputs are valid.
        """
        if self.operation == self.CREATE:
            # NOTE: Since in the case of a `CREATE`-transaction we do not have
            #       to check for outputs, we're just submitting dummy
            #       values to the actual method. This simplifies it's logic
            #       greatly, as we do not have to check against `None` values.
            return self._inputs_valid(['dummyvalue'
                                       for _ in self.inputs])
        elif self.operation == Transaction.TRANSFER:
            return self._inputs_valid([output.fulfillment.condition_uri
                                       for output in outputs])
        else:
            allowed_ops = ', '.join(self.__class__.ALLOWED_OPERATIONS)
            raise TypeError('`operation` must be one of {}'
                            .format(allowed_ops))

    def _inputs_valid(self, output_condition_uris):
        """Validates an Input against a given set of Outputs.

            Note:
                The number of `output_condition_uris` must be equal to the
                number of Inputs a Transaction has.

            Args:
                output_condition_uris (:obj:`list` of :obj:`str`): A list of
                    Outputs to check the Inputs against.

            Returns:
                bool: If all Outputs are valid.
        """

        if len(self.inputs) != len(output_condition_uris):
            raise ValueError('Inputs and '
                             'output_condition_uris must have the same count')

        tx_dict = self.to_dict()
        tx_dict = Transaction._remove_signatures(tx_dict)
        tx_dict['id'] = None
        tx_serialized = Transaction._to_str(tx_dict)

        def validate(i, output_condition_uri=None):
            """Validate input against output condition URI"""
            return self._input_valid(self.inputs[i], self.operation,
                                     tx_serialized, output_condition_uri)

        return all(validate(i, cond)
                   for i, cond in enumerate(output_condition_uris))

    def _input_valid(self, input_, operation, message, output_condition_uri=None):
        """Validates a single Input against a single Output.

            Note:
                In case of a `CREATE` Transaction, this method
                does not validate against `output_condition_uri`.

            Args:
                input_ (:class:`~bigchaindb.common.transaction.
                    Input`) The Input to be signed.
                operation (str): The type of Transaction.
                message (str): The fulfillment message.
                output_condition_uri (str, optional): An Output to check the
                    Input against.

            Returns:
                bool: If the Input is valid.
        """
        ccffill = input_.fulfillment
        try:
            parsed_ffill = Fulfillment.from_uri(ccffill.serialize_uri())
        except (TypeError, ValueError,
                ParsingError, ASN1DecodeError, ASN1EncodeError):
            return False

        if operation == self.CREATE:
            # NOTE: In the case of a `CREATE` transaction, the
            #       output is always valid.
            output_valid = True
        else:
            output_valid = output_condition_uri == ccffill.condition_uri

        message = sha3_256(message.encode())
        if input_.fulfills:
            message.update('{}{}'.format(
                input_.fulfills.txid, input_.fulfills.output).encode())

        # NOTE: We pass a timestamp to `.validate`, as in case of a timeout
        #       condition we'll have to validate against it

        # cryptoconditions makes no assumptions of the encoding of the
        # message to sign or verify. It only accepts bytestrings
        ffill_valid = parsed_ffill.validate(message=message.digest())
        return output_valid and ffill_valid

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Returns:
                dict: The Transaction as an alternative serialization format.
        """
        return {
            'inputs': [input_.to_dict() for input_ in self.inputs],
            'outputs': [output.to_dict() for output in self.outputs],
            'operation': str(self.operation),
            'metadata': self.metadata,
            'asset': self.asset,
            'version': self.version,
            'id': self._id,
        }

    @staticmethod
    # TODO: Remove `_dict` prefix of variable.
    def _remove_signatures(tx_dict):
        """Takes a Transaction dictionary and removes all signatures.

            Args:
                tx_dict (dict): The Transaction to remove all signatures from.

            Returns:
                dict

        """
        # NOTE: We remove the reference since we need `tx_dict` only for the
        #       transaction's hash
        tx_dict = deepcopy(tx_dict)
        for input_ in tx_dict['inputs']:
            # NOTE: Not all Cryptoconditions return a `signature` key (e.g.
            #       ThresholdSha256), so setting it to `None` in any
            #       case could yield incorrect signatures. This is why we only
            #       set it to `None` if it's set in the dict.
            input_['fulfillment'] = None
        return tx_dict

    @staticmethod
    def _to_hash(value):
        return hash_data(value)

    @property
    def id(self):
        return self._id

    def to_hash(self):
        return self.to_dict()['id']

    @staticmethod
    def _to_str(value):
        return serialize(value)

    # TODO: This method shouldn't call `_remove_signatures`
    def __str__(self):
        tx = Transaction._remove_signatures(self.to_dict())
        return Transaction._to_str(tx)

    @staticmethod
    def get_asset_id(transactions):
        """Get the asset id from a list of :class:`~.Transactions`.

        This is useful when we want to check if the multiple inputs of a
        transaction are related to the same asset id.

        Args:
            transactions (:obj:`list` of :class:`~bigchaindb.common.
                transaction.Transaction`): A list of Transactions.
                Usually input Transactions that should have a matching
                asset ID.

        Returns:
            str: ID of the asset.

        Raises:
            :exc:`AssetIdMismatch`: If the inputs are related to different
                assets.
        """

        if not isinstance(transactions, list):
            transactions = [transactions]

        # create a set of the transactions' asset ids
        asset_ids = {tx.id if tx.operation == Transaction.CREATE
                     else tx.asset['id']
                     for tx in transactions}

        # check that all the transasctions have the same asset id
        if len(asset_ids) > 1:
            raise AssetIdMismatch(('All inputs of all transactions passed'
                                   ' need to have the same asset id'))
        return asset_ids.pop()

    @staticmethod
    def validate_id(tx_body):
        """Validate the transaction ID of a transaction

            Args:
                tx_body (dict): The Transaction to be transformed.
        """
        # NOTE: Remove reference to avoid side effects
        tx_body = deepcopy(tx_body)
        try:
            proposed_tx_id = tx_body['id']
        except KeyError:
            raise InvalidHash('No transaction id found!')

        tx_body['id'] = None

        tx_body_serialized = Transaction._to_str(tx_body)
        valid_tx_id = Transaction._to_hash(tx_body_serialized)

        if proposed_tx_id != valid_tx_id:
            err_msg = ("The transaction's id '{}' isn't equal to "
                       "the hash of its body, i.e. it's not valid.")
            raise InvalidHash(err_msg.format(proposed_tx_id))

    @classmethod
    def from_dict(cls, tx, skip_schema_validation=True):
        """Transforms a Python dictionary to a Transaction object.

            Args:
                tx_body (dict): The Transaction to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.Transaction`
        """
        operation = tx.get('operation', Transaction.CREATE) if isinstance(tx, dict) else Transaction.CREATE
        cls = Transaction.resolve_class(operation)
        if not skip_schema_validation:
            cls.validate_schema(tx)

        inputs = [Input.from_dict(input_) for input_ in tx['inputs']]
        outputs = [Output.from_dict(output) for output in tx['outputs']]
        return cls(tx['operation'], tx['asset'], inputs, outputs,
                   tx['metadata'], tx['version'], hash_id=tx['id'])

    @classmethod
    def from_db(cls, bigchain, tx_dict_list):
        """Helper method that reconstructs a transaction dict that was returned
        from the database. It checks what asset_id to retrieve, retrieves the
        asset from the asset table and reconstructs the transaction.

        Args:
            bigchain (:class:`~bigchaindb.tendermint.BigchainDB`): An instance
                of BigchainDB used to perform database queries.
            tx_dict_list (:list:`dict` or :obj:`dict`): The transaction dict or
                list of transaction dict as returned from the database.

        Returns:
            :class:`~Transaction`

        """
        return_list = True
        if isinstance(tx_dict_list, dict):
            tx_dict_list = [tx_dict_list]
            return_list = False

        tx_map = {}
        tx_ids = []
        for tx in tx_dict_list:
            tx.update({'metadata': None})
            tx_map[tx['id']] = tx
            tx_ids.append(tx['id'])

        assets = list(bigchain.get_assets(tx_ids))
        for asset in assets:
            if asset is not None:
                tx = tx_map[asset['id']]
                del asset['id']
                tx['asset'] = asset

        tx_ids = list(tx_map.keys())
        metadata_list = list(bigchain.get_metadata(tx_ids))
        for metadata in metadata_list:
            tx = tx_map[metadata['id']]
            tx.update({'metadata': metadata.get('metadata')})

        if return_list:
            tx_list = []
            for tx_id, tx in tx_map.items():
                tx_list.append(cls.from_dict(tx))
            return tx_list
        else:
            tx = list(tx_map.values())[0]
            return cls.from_dict(tx)

    type_registry = {}

    @staticmethod
    def register_type(tx_type, tx_class):
        Transaction.type_registry[tx_type] = tx_class

    def resolve_class(operation):
        """For the given `tx` based on the `operation` key return its implementation class"""

        create_txn_class = Transaction.type_registry.get(Transaction.CREATE)
        return Transaction.type_registry.get(operation, create_txn_class)

    @classmethod
    def validate_schema(cls, tx):
        pass
