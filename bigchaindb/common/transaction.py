from copy import deepcopy
from functools import reduce
from uuid import uuid4

from cryptoconditions import (Fulfillment as CCFulfillment,
                              ThresholdSha256Fulfillment, Ed25519Fulfillment)
from cryptoconditions.exceptions import ParsingError

from bigchaindb.common.crypto import PrivateKey, hash_data
from bigchaindb.common.exceptions import (KeypairMismatchException,
                                          InvalidHash, InvalidSignature,
                                          AmountError, AssetIdMismatch)
from bigchaindb.common.util import serialize, gen_timestamp


class Input(object):
    """A Input is used to spend assets locked by an Output.

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
        """Fulfillment shims a Cryptocondition Fulfillment for BigchainDB.

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
        except (TypeError, AttributeError):
            # NOTE: When a non-signed transaction is casted to a dict,
            #       `self.inputs` value is lost, as in the node's
            #       transaction model that is saved to the database, does not
            #       account for its dictionary form but just for its signed uri
            #       form.
            #       Hence, when a non-signed fulfillment is to be cast to a
            #       dict, we just call its internal `to_dict` method here and
            #       its `from_dict` method in `Fulfillment.from_dict`.
            fulfillment = self.fulfillment.to_dict()

        try:
            # NOTE: `self.fulfills` can be `None` and that's fine
            fulfills = self.fulfills.to_dict()
        except AttributeError:
            fulfills = None

        input = {
            'owners_before': self.owners_before,
            'fulfills': fulfills,
            'fulfillment': fulfillment,
        }
        return input

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
                data (dict): The Fulfillment to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.Input`

            Raises:
                InvalidSignature: If an Input's URI couldn't be parsed.
        """
        try:
            fulfillment = CCFulfillment.from_uri(data['fulfillment'])
        except ValueError:
            # TODO FOR CC: Throw an `InvalidSignature` error in this case.
            raise InvalidSignature("Fulfillment URI couldn't been parsed")
        except TypeError:
            # NOTE: See comment about this special case in
            #       `Input.to_dict`
            fulfillment = CCFulfillment.from_dict(data['fulfillment'])
        fulfills = TransactionLink.from_dict(data['fulfills'])
        return cls(fulfillment, data['owners_before'], fulfills)


class TransactionLink(object):
    """An object for unidirectional linking to a Transaction's Condition.

        Attributes:
            txid (str, optional): A Transaction to link to.
            idx (int, optional): An output's index in a Transaction with id
            `txid`.
    """

    def __init__(self, txid=None, idx=None):
        """Used to point to a specific Condition of a Transaction.

            Note:
                In an IPLD implementation, this class is not necessary anymore,
                as an IPLD link can simply point to an object, as well as an
                objects properties. So instead of having a (de)serializable
                class, we can have a simple IPLD link of the form:
                `/<tx_id>/transaction/outputs/<idx>/`.

            Args:
                txid (str, optional): A Transaction to link to.
                idx (int, optional): An Outputs's index in a Transaction with
                    id `txid`.
        """
        self.txid = txid
        self.idx = idx

    def __bool__(self):
        return self.txid is not None and self.idx is not None

    def __eq__(self, other):
        # TODO: If `other !== TransactionLink` return `False`
        return self.to_dict() == self.to_dict()

    @classmethod
    def from_dict(cls, link):
        """Transforms a Python dictionary to a TransactionLink object.

            Args:
                link (dict): The link to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.TransactionLink`
        """
        try:
            return cls(link['txid'], link['idx'])
        except TypeError:
            return cls()

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Returns:
                (dict|None): The link as an alternative serialization format.
        """
        if self.txid is None and self.idx is None:
            return None
        else:
            return {
                'txid': self.txid,
                'idx': self.idx,
            }

    def to_uri(self, path=''):
        if self.txid is None and self.cid is None:
            return None
        return '{}/transactions/{}/conditions/{}'.format(path, self.txid,
                                                         self.cid)


class Output(object):
    """An Output is used to lock an asset.

        Attributes:
            fulfillment (:class:`cryptoconditions.Fulfillment`): A Fulfillment
                to extract a Condition from.
            owners_after (:obj:`list` of :obj:`str`, optional): A list of
                owners before a Transaction was confirmed.
    """

    def __init__(self, fulfillment, public_keys=None, amount=1):
        """Condition shims a Cryptocondition condition for BigchainDB.

            Args:
                fulfillment (:class:`cryptoconditions.Fulfillment`): A
                    Fulfillment to extract a Condition from.
                public_keys (:obj:`list` of :obj:`str`, optional): A list of
                    owners before a Transaction was confirmed.
                amount (int): The amount of Assets to be locked with this
                    Condition.

            Raises:
                TypeError: if `public_keys` is not instance of `list`.
        """
        if not isinstance(public_keys, list) and public_keys is not None:
            raise TypeError('`public_keys` must be a list instance or None')

        self.fulfillment = fulfillment
        # TODO: Not sure if we should validate for value here
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
            condition['details'] = self.fulfillment.to_dict()
        except AttributeError:
            pass

        try:
            condition['uri'] = self.fulfillment.condition_uri
        except AttributeError:
            condition['uri'] = self.fulfillment

        output = {
            'public_keys': self.public_keys,
            'condition': condition,
            'amount': self.amount
        }
        return output

    @classmethod
    def generate(cls, public_keys, amount):
        """Generates a Condition from a specifically formed tuple or list.

            Note:
                If a ThresholdCondition has to be generated where the threshold
                is always the number of subconditions it is split between, a
                list of the following structure is sufficient:

                [(address|condition)*, [(address|condition)*, ...], ...]

            Args:
                public_keys (:obj:`list` of :obj:`str`): The public key of
                    the users that should be able to fulfill the Condition
                    that is being created.
                amount (:obj:`int`): The amount locked by the condition.

            Returns:
                A Condition that can be used in a Transaction.

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
            try:
                ffill = Ed25519Fulfillment(public_key=public_keys[0])
            except TypeError:
                ffill = public_keys[0]
            return cls(ffill, public_keys, amount=amount)
        else:
            initial_cond = ThresholdSha256Fulfillment(threshold=threshold)
            threshold_cond = reduce(cls._gen_condition, public_keys,
                                    initial_cond)
            return cls(threshold_cond, public_keys, amount=amount)

    @classmethod
    def _gen_condition(cls, initial, current):
        """Generates ThresholdSha256 conditions from a list of new owners.

            Note:
                This method is intended only to be used with a reduce function.
                For a description on how to use this method, see
                `Condition.generate`.

            Args:
                initial (:class:`cryptoconditions.ThresholdSha256Fulfillment`):
                    A Condition representing the overall root.
                current (:obj:`list` of :obj:`str`|str): A list of new owners
                    or a single new owner.

            Returns:
                :class:`cryptoconditions.ThresholdSha256Fulfillment`:
        """
        owners_after = current
        try:
            threshold = len(owners_after)
        except TypeError:
            threshold = None

        if isinstance(owners_after, list) and len(owners_after) > 1:
            ffill = ThresholdSha256Fulfillment(threshold=threshold)
            reduce(cls._gen_condition, owners_after, ffill)
        elif isinstance(owners_after, list) and len(owners_after) <= 1:
            raise ValueError('Sublist cannot contain single owner')
        else:
            try:
                owners_after = owners_after.pop()
            except AttributeError:
                pass
            try:
                ffill = Ed25519Fulfillment(public_key=owners_after)
            except TypeError:
                # NOTE: Instead of submitting base58 encoded addresses, a user
                #       of this class can also submit fully instantiated
                #       Cryptoconditions. In the case of casting `owners_after`
                #       to a Ed25519Fulfillment with the result of a
                #       `TypeError`, we're assuming that `owners_after` is a
                #       Cryptocondition then.
                ffill = owners_after
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
            fulfillment = CCFulfillment.from_dict(data['condition']['details'])
        except KeyError:
            # NOTE: Hashlock condition case
            fulfillment = data['condition']['uri']
        return cls(fulfillment, data['public_keys'], data['amount'])


class Asset(object):
    """An Asset is a fungible unit to spend and lock with Transactions.

        Note:
            Currently, the following flags are not yet fully supported:
                - `divisible`
                - `updatable`
                - `refillable`

        Attributes:
            data (dict): A dictionary of data that can be added to an Asset.
            data_id (str): A unique identifier of `data`'s content.
            divisible (bool): A flag indicating if an Asset can be divided.
            updatable (bool): A flag indicating if an Asset can be updated.
            refillable (bool): A flag indicating if an Asset can be refilled.
    """

    def __init__(self, data=None, data_id=None, divisible=False,
                 updatable=False, refillable=False):
        """An Asset is not required to contain any extra data from outside."""
        self.data = data
        self.data_id = data_id if data_id is not None else self.to_hash()
        self.divisible = divisible
        self.updatable = updatable
        self.refillable = refillable

        self.validate_asset()

    def __eq__(self, other):
        try:
            other_dict = other.to_dict()
        except AttributeError:
            return False
        return self.to_dict() == other_dict

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Returns:
                (dict): The Asset object as an alternative serialization
                    format.
        """
        return {
            'id': self.data_id,
            'divisible': self.divisible,
            'updatable': self.updatable,
            'refillable': self.refillable,
            'data': self.data,
        }

    @classmethod
    def from_dict(cls, asset):
        """Transforms a Python dictionary to an Asset object.

            Args:
                asset (dict): The dictionary to be serialized.

            Returns:
                :class:`~bigchaindb.common.transaction.Asset`
        """
        return cls(asset.get('data'), asset['id'],
                   asset.get('divisible', False),
                   asset.get('updatable', False),
                   asset.get('refillable', False))

    def to_hash(self):
        """Generates a unqiue uuid for an Asset"""
        return str(uuid4())

    @staticmethod
    def get_asset_id(transactions):
        """Get the asset id from a list of transaction ids.

        This is useful when we want to check if the multiple inputs of a
        transaction are related to the same asset id.

        Args:
            transactions (:obj:`list` of :class:`~bigchaindb.common.
                transaction.Transaction`): list of transaction usually inputs
                that should have a matching asset_id

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
            raise AssetIdMismatch(('All inputs of all transactions passed'
                                   ' need to have the same asset id'))
        return asset_ids.pop()

    def validate_asset(self, amount=None):
        """Validates the asset"""
        if self.data is not None and not isinstance(self.data, dict):
            raise TypeError('`data` must be a dict instance or None')
        if not isinstance(self.divisible, bool):
            raise TypeError('`divisible` must be a boolean')
        if not isinstance(self.refillable, bool):
            raise TypeError('`refillable` must be a boolean')
        if not isinstance(self.updatable, bool):
            raise TypeError('`updatable` must be a boolean')

        if self.refillable:
            raise NotImplementedError('Refillable assets are not yet'
                                      ' implemented')
        if self.updatable:
            raise NotImplementedError('Updatable assets are not yet'
                                      ' implemented')

        # If the amount is supplied we can perform extra validations to
        # the asset
        if amount is not None:
            if not isinstance(amount, int):
                raise TypeError('`amount` must be an int')

            if self.divisible is False and amount != 1:
                raise AmountError('non divisible assets always have'
                                  ' amount equal to one')

            # Since refillable assets are not yet implemented this should
            # raise and exception
            if self.divisible is True and amount < 2:
                raise AmountError('divisible assets must have an amount'
                                  ' greater than one')


class AssetLink(Asset):
    """An object for unidirectional linking to a Asset.
    """

    def __init__(self, data_id=None):
        """Used to point to a specific Asset.

            Args:
                data_id (str): A Asset to link to.
        """
        self.data_id = data_id

    def __bool__(self):
        return self.data_id is not None

    def __eq__(self, other):
        return isinstance(other, AssetLink) and \
                self.to_dict() == other.to_dict()

    @classmethod
    def from_dict(cls, link):
        """Transforms a Python dictionary to a AssetLink object.

            Args:
                link (dict): The link to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.AssetLink`
        """
        try:
            return cls(link['id'])
        except TypeError:
            return cls()

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Returns:
                (dict|None): The link as an alternative serialization format.
        """
        if self.data_id is None:
            return None
        else:
            return {
                'id': self.data_id
            }


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
            metadata (dict):
                Metadata to be stored along with the Transaction.
            version (int): Defines the version number of a Transaction.
    """
    CREATE = 'CREATE'
    TRANSFER = 'TRANSFER'
    GENESIS = 'GENESIS'
    ALLOWED_OPERATIONS = (CREATE, TRANSFER, GENESIS)
    VERSION = 1

    def __init__(self, operation, asset, inputs=None, outputs=None,
                 metadata=None, version=None):
        """The constructor allows to create a customizable Transaction.

            Note:
                When no `version` is provided, one is being
                generated by this method.

            Args:
                operation (str): Defines the operation of the Transaction.
                asset (:class:`~bigchaindb.common.transaction.Asset`): An Asset
                    to be transferred or created in a Transaction.
                inputs (:obj:`list` of :class:`~bigchaindb.common.
                    transaction.Fulfillment`, optional): Define the assets to
                    spend.
                outputs (:obj:`list` of :class:`~bigchaindb.common.
                    transaction.Condition`, optional): Define the assets to
                    lock.
                metadata (dict):
                    Metadata to be stored along with the Transaction.
                version (int): Defines the version number of a Transaction.

        """
        if operation not in Transaction.ALLOWED_OPERATIONS:
            allowed_ops = ', '.join(self.__class__.ALLOWED_OPERATIONS)
            raise ValueError('`operation` must be one of {}'
                             .format(allowed_ops))

        # Only assets for 'CREATE' operations can be un-defined.
        if (asset and not isinstance(asset, Asset) or
                not asset and operation != Transaction.CREATE):
            raise TypeError('`asset` must be an Asset instance')

        if outputs and not isinstance(outputs, list):
            raise TypeError('`outputs` must be a list instance or None')

        if inputs and not isinstance(inputs, list):
            raise TypeError('`inputs` must be a list instance or None')

        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError('`metadata` must be a dict or None')

        self.version = version if version is not None else self.VERSION
        self.operation = operation
        self.asset = asset if asset else Asset()
        self.outputs = outputs if outputs else []
        self.inputs = inputs if inputs else []
        self.metadata = metadata

        # validate asset
        # we know that each transaction relates to a single asset
        # we can sum the amount of all the outputs
        # for transactions other then CREATE we only have an id so there is
        # nothing we can validate
        if self.operation == self.CREATE:
            amount = sum([condition.amount for condition in self.outputs])
            self.asset.validate_asset(amount=amount)

    @classmethod
    def create(cls, creators, recipients, metadata=None, asset=None):
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
                creators (:obj:`list` of :obj:`str`): A list of keys that
                    represent the creators of this Transaction.
                recipients (:obj:`list` of :obj:`str`): A list of keys that
                    represent the recipients of this Transaction.
                metadata (dict): Python dictionary to be stored along with the
                    Transaction.
                asset (:class:`~bigchaindb.common.transaction.Asset`): An Asset
                    to be created in this Transaction.

            Returns:
                :class:`~bigchaindb.common.transaction.Transaction`
        """
        if not isinstance(creators, list):
            raise TypeError('`creators` must be a list instance')
        if not isinstance(recipients, list):
            raise TypeError('`recipients` must be a list instance')
        if len(creators) == 0:
            raise ValueError('`creators` list cannot be empty')
        if len(recipients) == 0:
            raise ValueError('`recipients` list cannot be empty')

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
        inputs.append(Input.generate(creators))

        return cls(cls.CREATE, asset, inputs, outputs, metadata)

    @classmethod
    def transfer(cls, inputs, recipients, asset, metadata=None):
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
                recipients (:obj:`list` of :obj:`str`): A list of
                    ([keys],amount) that represent the recipients of this
                    Transaction.
                asset (:class:`~bigchaindb.common.transaction.Asset`): An Asset
                    to be transferred in this Transaction.
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

        inputs = deepcopy(inputs)
        return cls(cls.TRANSFER, asset, inputs, outputs, metadata)

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
        indices = indices or range(len(self.outputs))
        return [
            Input(self.outputs[idx].fulfillment,
                  self.outputs[idx].public_keys,
                  TransactionLink(self.id, idx))
            for idx in indices
        ]

    def add_input(self, input):
        """Adds an input to a Transaction's list of inputs.

            Args:
                fulfillment (:class:`~bigchaindb.common.transaction.
                    Input`): An Input to be added to the Transaction.
        """
        if not isinstance(input, Input):
            raise TypeError('`input` must be a Input instance')
        self.inputs.append(input)

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
                    - ThresholdSha256Fulfillment
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

        for index, input in enumerate(self.inputs):
            # NOTE: We clone the current transaction but only add the output
            #       and input we're currently working on plus all
            #       previously signed ones.
            tx_partial = Transaction(self.operation, self.asset, [input],
                                     self.outputs, self.metadata,
                                     self.version)

            tx_partial_dict = tx_partial.to_dict()
            tx_partial_dict = Transaction._remove_signatures(tx_partial_dict)
            tx_serialized = Transaction._to_str(tx_partial_dict)
            self._sign_input(input, index, tx_serialized, key_pairs)
        return self

    def _sign_input(self, input, index, tx_serialized, key_pairs):
        """Signs a single Input with a partial Transaction as message.

            Note:
                This method works only for the following Cryptoconditions
                currently:
                    - Ed25519Fulfillment
                    - ThresholdSha256Fulfillment.

            Args:
                input (:class:`~bigchaindb.common.transaction.
                    Input`) The Input to be signed.
                index (int): The index of the input to be signed.
                tx_serialized (str): The Transaction to be used as message.
                key_pairs (dict): The keys to sign the Transaction with.
        """
        if isinstance(input.fulfillment, Ed25519Fulfillment):
            self._sign_simple_signature_fulfillment(input, index,
                                                    tx_serialized, key_pairs)
        elif isinstance(input.fulfillment, ThresholdSha256Fulfillment):
            self._sign_threshold_signature_fulfillment(input, index,
                                                       tx_serialized,
                                                       key_pairs)
        else:
            raise ValueError("Fulfillment couldn't be matched to "
                             'Cryptocondition fulfillment type.')

    def _sign_simple_signature_fulfillment(self, input, index,
                                           tx_serialized, key_pairs):
        """Signs a Ed25519Fulfillment.

            Args:
                input (:class:`~bigchaindb.common.transaction.
                    Input`) The input to be signed.
                index (int): The index of the input to be
                    signed.
                tx_serialized (str): The Transaction to be used as message.
                key_pairs (dict): The keys to sign the Transaction with.
        """
        # NOTE: To eliminate the dangers of accidentally signing a condition by
        #       reference, we remove the reference of input here
        #       intentionally. If the user of this class knows how to use it,
        #       this should never happen, but then again, never say never.
        input = deepcopy(input)
        public_key = input.owners_before[0]
        try:
            # cryptoconditions makes no assumptions of the encoding of the
            # message to sign or verify. It only accepts bytestrings
            input.fulfillment.sign(tx_serialized.encode(), key_pairs[public_key])
        except KeyError:
            raise KeypairMismatchException('Public key {} is not a pair to '
                                           'any of the private keys'
                                           .format(public_key))
        self.inputs[index] = input

    def _sign_threshold_signature_fulfillment(self, input, index,
                                              tx_serialized, key_pairs):
        """Signs a ThresholdSha256Fulfillment.

            Args:
                input (:class:`~bigchaindb.common.transaction.
                    Input`) The Input to be signed.
                index (int): The index of the Input to be
                    signed.
                tx_serialized (str): The Transaction to be used as message.
                key_pairs (dict): The keys to sign the Transaction with.
        """
        input = deepcopy(input)
        for owner_before in input.owners_before:
            try:
                # TODO: CC should throw a KeypairMismatchException, instead of
                #       our manual mapping here

                # TODO FOR CC: Naming wise this is not so smart,
                #              `get_subcondition` in fact doesn't return a
                #              condition but a fulfillment

                # TODO FOR CC: `get_subcondition` is singular. One would not
                #              expect to get a list back.
                ccffill = input.fulfillment
                subffill = ccffill.get_subcondition_from_vk(owner_before)[0]
            except IndexError:
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
            subffill.sign(tx_serialized.encode(), private_key)
        self.inputs[index] = input

    def inputs_valid(self, outputs=None):
        """Validates the Inputs in the Transaction against given
        Outputs.

            Note:
                Given a `CREATE` or `GENESIS` Transaction is passed,
                dummyvalues for Outputs are submitted for validation that
                evaluate parts of the validation-checks to `True`.

            Args:
                outputs (:obj:`list` of :class:`~bigchaindb.common.
                    transaction.Output`): A list of Outputs to check the
                    Inputs against.

            Returns:
                bool: If all Inputs are valid.
        """
        if self.operation in (Transaction.CREATE, Transaction.GENESIS):
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

    def _inputs_valid(self, output_uris):
        """Validates an Input against a given set of Outputs.

            Note:
                The number of `output_uris` must be equal to the
                number of Inputs a Transaction has.

            Args:
                output_uris (:obj:`list` of :obj:`str`): A list of
                    Outputs to check the Inputs against.

            Returns:
                bool: If all Outputs are valid.
        """

        if len(self.inputs) != len(output_uris):
            raise ValueError('Inputs and '
                             'output_uris must have the same count')

        def gen_tx(input, output, output_uri=None):
            """Splits multiple IO Transactions into partial single IO
            Transactions.
            """
            tx = Transaction(self.operation, self.asset, [input],
                             self.outputs, self.metadata, self.version)
            tx_dict = tx.to_dict()
            tx_dict = Transaction._remove_signatures(tx_dict)
            tx_serialized = Transaction._to_str(tx_dict)

            # TODO: Use local reference to class, not `Transaction.`
            return Transaction._input_valid(input, self.operation,
                                            tx_serialized, output_uri)

        partial_transactions = map(gen_tx, self.inputs,
                                   self.outputs, output_uris)
        return all(partial_transactions)

    @staticmethod
    def _input_valid(input, operation, tx_serialized, output_uri=None):
        """Validates a single Input against a single Output.

            Note:
                In case of a `CREATE` or `GENESIS` Transaction, this method
                does not validate against `output_uri`.

            Args:
                input (:class:`~bigchaindb.common.transaction.
                    Input`) The Input to be signed.
                operation (str): The type of Transaction.
                tx_serialized (str): The Transaction used as a message when
                    initially signing it.
                output_uri (str, optional): An Output to check the
                    Input against.

            Returns:
                bool: If the Input is valid.
        """
        ccffill = input.fulfillment
        try:
            parsed_ffill = CCFulfillment.from_uri(ccffill.serialize_uri())
        except (TypeError, ValueError, ParsingError):
            return False

        if operation in (Transaction.CREATE, Transaction.GENESIS):
            # NOTE: In the case of a `CREATE` or `GENESIS` transaction, the
            #       output is always validate to `True`.
            output_valid = True
        else:
            output_valid = output_uri == ccffill.condition_uri

        # NOTE: We pass a timestamp to `.validate`, as in case of a timeout
        #       condition we'll have to validate against it

        # cryptoconditions makes no assumptions of the encoding of the
        # message to sign or verify. It only accepts bytestrings
        ffill_valid = parsed_ffill.validate(message=tx_serialized.encode(),
                                            now=gen_timestamp())
        return output_valid and ffill_valid

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Returns:
                dict: The Transaction as an alternative serialization format.
        """
        if self.operation in (self.__class__.GENESIS, self.__class__.CREATE):
            asset = self.asset.to_dict()
        else:
            # NOTE: An `asset` in a `TRANSFER` only contains the asset's id
            asset = {'id': self.asset.data_id}

        tx = {
            'inputs': [input.to_dict() for input in self.inputs],
            'outputs': [output.to_dict() for output in self.outputs],
            'operation': str(self.operation),
            'metadata': self.metadata,
            'asset': asset,
            'version': self.version,
        }

        tx_no_signatures = Transaction._remove_signatures(tx)
        tx_serialized = Transaction._to_str(tx_no_signatures)
        tx_id = Transaction._to_hash(tx_serialized)

        tx['id'] = tx_id
        return tx

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
        for input in tx_dict['inputs']:
            # NOTE: Not all Cryptoconditions return a `signature` key (e.g.
            #       ThresholdSha256Fulfillment), so setting it to `None` in any
            #       case could yield incorrect signatures. This is why we only
            #       set it to `None` if it's set in the dict.
            input['fulfillment'] = None
        return tx_dict

    @staticmethod
    def _to_hash(value):
        return hash_data(value)

    @property
    def id(self):
        return self.to_hash()

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
    def validate_structure(tx_body):
        """Validate the transaction ID of a transaction

            Args:
                tx_body (dict): The Transaction to be transformed.
        """
        # NOTE: Remove reference to avoid side effects
        tx_body = deepcopy(tx_body)
        try:
            proposed_tx_id = tx_body.pop('id')
        except KeyError:
            raise InvalidHash('No transaction id found!')

        tx_body_no_signatures = Transaction._remove_signatures(tx_body)
        tx_body_serialized = Transaction._to_str(tx_body_no_signatures)
        valid_tx_id = Transaction._to_hash(tx_body_serialized)

        if proposed_tx_id != valid_tx_id:
            err_msg = ("The transaction's id '{}' isn't equal to "
                       "the hash of its body, i.e. it's not valid.")
            raise InvalidHash(err_msg.format(proposed_tx_id))

    @classmethod
    def from_dict(cls, tx):
        """Transforms a Python dictionary to a Transaction object.

            Args:
                tx_body (dict): The Transaction to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.Transaction`
        """
        cls.validate_structure(tx)
        inputs = [Input.from_dict(input) for input in tx['inputs']]
        outputs = [Output.from_dict(output) for output in tx['outputs']]
        if tx['operation'] in [cls.CREATE, cls.GENESIS]:
            asset = Asset.from_dict(tx['asset'])
        else:
            asset = AssetLink.from_dict(tx['asset'])

        return cls(tx['operation'], asset, inputs, outputs,
                   tx['metadata'], tx['version'])
