from copy import deepcopy
from functools import reduce

from cryptoconditions import (Fulfillment as CCFulfillment,
                              ThresholdSha256Fulfillment, Ed25519Fulfillment)
from cryptoconditions.exceptions import ParsingError

from bigchaindb.common.crypto import PrivateKey, hash_data
from bigchaindb.common.exceptions import (KeypairMismatchException,
                                          InvalidHash, InvalidSignature,
                                          AmountError, AssetIdMismatch)
from bigchaindb.common.util import serialize, gen_timestamp


class Fulfillment(object):
    """A Fulfillment is used to spend assets locked by a Condition.

        Attributes:
            fulfillment (:class:`cryptoconditions.Fulfillment`): A Fulfillment
                to be signed with a private key.
            owners_before (:obj:`list` of :obj:`str`): A list of owners after a
                Transaction was confirmed.
            tx_input (:class:`~bigchaindb.common.transaction. TransactionLink`,
                optional): A link representing the input of a `TRANSFER`
                Transaction.
    """

    def __init__(self, fulfillment, owners_before, tx_input=None):
        """Fulfillment shims a Cryptocondition Fulfillment for BigchainDB.

            Args:
                fulfillment (:class:`cryptoconditions.Fulfillment`): A
                    Fulfillment to be signed with a private key.
                owners_before (:obj:`list` of :obj:`str`): A list of owners
                    after a Transaction was confirmed.
                tx_input (:class:`~bigchaindb.common.transaction.
                    TransactionLink`, optional): A link representing the input
                    of a `TRANSFER` Transaction.
        """
        if tx_input is not None and not isinstance(tx_input, TransactionLink):
            raise TypeError('`tx_input` must be a TransactionLink instance')

        if not isinstance(owners_before, list):
            raise TypeError('`owners_after` must be a list instance')

        self.fulfillment = fulfillment
        self.tx_input = tx_input
        self.owners_before = owners_before

    def __eq__(self, other):
        # TODO: If `other !== Fulfillment` return `False`
        return self.to_dict() == other.to_dict()

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Note:
                If a Fulfillment hasn't been signed yet, this method returns a
                dictionary representation.

            Returns:
                dict: The Fulfillment as an alternative serialization format.
        """
        try:
            fulfillment = self.fulfillment.serialize_uri()
        except (TypeError, AttributeError):
            # NOTE: When a non-signed transaction is casted to a dict,
            #       `self.fulfillments` value is lost, as in the node's
            #       transaction model that is saved to the database, does not
            #       account for its dictionary form but just for its signed uri
            #       form.
            #       Hence, when a non-signed fulfillment is to be cast to a
            #       dict, we just call its internal `to_dict` method here and
            #       its `from_dict` method in `Fulfillment.from_dict`.
            fulfillment = self.fulfillment.to_dict()

        try:
            # NOTE: `self.tx_input` can be `None` and that's fine
            tx_input = self.tx_input.to_dict()
        except AttributeError:
            tx_input = None

        ffill = {
            'owners_before': self.owners_before,
            'input': tx_input,
            'fulfillment': fulfillment,
        }
        return ffill

    @classmethod
    def generate(cls, owners_before):
        # TODO: write docstring
        # The amount here does not really matter. It is only use on the
        # condition data model but here we only care about the fulfillment
        condition = Condition.generate(owners_before, 1)
        return cls(condition.fulfillment, condition.owners_after)

    @classmethod
    def from_dict(cls, ffill):
        """Transforms a Python dictionary to a Fulfillment object.

            Note:
                Optionally, this method can also serialize a Cryptoconditions-
                Fulfillment that is not yet signed.

            Args:
                ffill (dict): The Fulfillment to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.Fulfillment`

            Raises:
                InvalidSignature: If a Fulfillment's URI couldn't be parsed.
        """
        try:
            fulfillment = CCFulfillment.from_uri(ffill['fulfillment'])
        except ValueError:
            # TODO FOR CC: Throw an `InvalidSignature` error in this case.
            raise InvalidSignature("Fulfillment URI couldn't been parsed")
        except TypeError:
            # NOTE: See comment about this special case in
            #       `Fulfillment.to_dict`
            fulfillment = CCFulfillment.from_dict(ffill['fulfillment'])
        input_ = TransactionLink.from_dict(ffill['input'])
        return cls(fulfillment, ffill['owners_before'], input_)


class TransactionLink(object):
    """An object for unidirectional linking to a Transaction's Condition.

        Attributes:
            txid (str, optional): A Transaction to link to.
            cid (int, optional): A Condition's index in a Transaction with id
            `txid`.
    """

    def __init__(self, txid=None, cid=None):
        """Used to point to a specific Condition of a Transaction.

            Note:
                In an IPLD implementation, this class is not necessary anymore,
                as an IPLD link can simply point to an object, as well as an
                objects properties. So instead of having a (de)serializable
                class, we can have a simple IPLD link of the form:
                `/<tx_id>/transaction/conditions/<cid>/`.

            Args:
                txid (str, optional): A Transaction to link to.
                cid (int, optional): A Condition's index in a Transaction with
                    id `txid`.
        """
        self.txid = txid
        self.cid = cid

    def __bool__(self):
        return self.txid is not None and self.cid is not None

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
            return cls(link['txid'], link['cid'])
        except TypeError:
            return cls()

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Returns:
                (dict|None): The link as an alternative serialization format.
        """
        if self.txid is None and self.cid is None:
            return None
        else:
            return {
                'txid': self.txid,
                'cid': self.cid,
            }

    def to_uri(self, path=''):
        if self.txid is None and self.cid is None:
            return None
        return '{}/transactions/{}/conditions/{}'.format(path, self.txid,
                                                         self.cid)


class Condition(object):
    """A Condition is used to lock an asset.

        Attributes:
            fulfillment (:class:`cryptoconditions.Fulfillment`): A Fulfillment
                to extract a Condition from.
            owners_after (:obj:`list` of :obj:`str`, optional): A list of
                owners before a Transaction was confirmed.
    """

    def __init__(self, fulfillment, owners_after=None, amount=1):
        """Condition shims a Cryptocondition condition for BigchainDB.

            Args:
                fulfillment (:class:`cryptoconditions.Fulfillment`): A
                    Fulfillment to extract a Condition from.
                owners_after (:obj:`list` of :obj:`str`, optional): A list of
                    owners before a Transaction was confirmed.
                amount (int): The amount of Assets to be locked with this
                    Condition.

            Raises:
                TypeError: if `owners_after` is not instance of `list`.
        """
        if not isinstance(owners_after, list) and owners_after is not None:
            raise TypeError('`owners_after` must be a list instance or None')

        self.fulfillment = fulfillment
        # TODO: Not sure if we should validate for value here
        self.amount = amount
        self.owners_after = owners_after

    def __eq__(self, other):
        # TODO: If `other !== Condition` return `False`
        return self.to_dict() == other.to_dict()

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Note:
                A dictionary serialization of the Fulfillment the Condition was
                derived from is always provided.

            Returns:
                dict: The Condition as an alternative serialization format.
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

        cond = {
            'owners_after': self.owners_after,
            'condition': condition,
            'amount': self.amount
        }
        return cond

    @classmethod
    def generate(cls, owners_after, amount):
        """Generates a Condition from a specifically formed tuple or list.

            Note:
                If a ThresholdCondition has to be generated where the threshold
                is always the number of subconditions it is split between, a
                list of the following structure is sufficient:

                [(address|condition)*, [(address|condition)*, ...], ...]

            Args:
                owners_after (:obj:`list` of :obj:`str`): The public key of
                    the users that should be able to fulfill the Condition
                    that is being created.
                amount (:obj:`int`): The amount locked by the condition.

            Returns:
                A Condition that can be used in a Transaction.

            Raises:
                TypeError: If `owners_after` is not an instance of `list`.
                ValueError: If `owners_after` is an empty list.
        """
        threshold = len(owners_after)
        if not isinstance(amount, int):
            raise TypeError('`amount` must be a int')
        if amount < 1:
            raise AmountError('`amount` needs to be greater than zero')
        if not isinstance(owners_after, list):
            raise TypeError('`owners_after` must be an instance of list')
        if len(owners_after) == 0:
            raise ValueError('`owners_after` needs to contain at least one'
                             'owner')
        elif len(owners_after) == 1 and not isinstance(owners_after[0], list):
            try:
                ffill = Ed25519Fulfillment(public_key=owners_after[0])
            except TypeError:
                ffill = owners_after[0]
            return cls(ffill, owners_after, amount=amount)
        else:
            initial_cond = ThresholdSha256Fulfillment(threshold=threshold)
            threshold_cond = reduce(cls._gen_condition, owners_after,
                                    initial_cond)
            return cls(threshold_cond, owners_after, amount=amount)

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
    def from_dict(cls, cond):
        """Transforms a Python dictionary to a Condition object.

            Note:
                To pass a serialization cycle multiple times, a
                Cryptoconditions Fulfillment needs to be present in the
                passed-in dictionary, as Condition URIs are not serializable
                anymore.

            Args:
                cond (dict): The Condition to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.Condition`
        """
        try:
            fulfillment = CCFulfillment.from_dict(cond['condition']['details'])
        except KeyError:
            # NOTE: Hashlock condition case
            fulfillment = cond['condition']['uri']
        return cls(fulfillment, cond['owners_after'], cond['amount'])


class Asset(object):
    """An Asset is a fungible unit to spend and lock with Transactions.

        Attributes:
            data (dict): A dictionary of data that can be added to an Asset.
    """

    def __init__(self, data=None):
        """An Asset is not required to contain any extra data from outside."""
        self.data = data
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
        return cls(asset.get('data'))

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
        asset_ids = {tx.id if tx.operation == Transaction.CREATE else tx.asset.id
                     for tx in transactions}

        # check that all the transasctions have the same asset id
        if len(asset_ids) > 1:
            raise AssetIdMismatch(('All inputs of all transactions passed'
                                   ' need to have the same asset id'))
        return asset_ids.pop()

    def validate_asset(self, amount=None):
        """Validates the asset"""
        if self.data is not None and not isinstance(self.data, dict):
            raise TypeError('`data` must be a dict instance or None')

        # If the amount is supplied we can perform extra validations to
        # the asset
        if amount is not None:
            if not isinstance(amount, int):
                raise TypeError('`amount` must be an int')

            if amount < 1:
                raise AmountError('`amount` must be greater than 0')


class AssetLink(object):
    """An object for unidirectional linking to a Asset.
    """

    def __init__(self, asset_id=None):
        """Used to point to a specific Asset.

            Args:
                asset_id (str): The ID of an asset to link to.
        """
        self.id = asset_id

    def __bool__(self):
        return self.id is not None

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
                    Returns None if the link is empty (i.e. is not linking to
                    an asset).
        """
        if self.id is None:
            return None
        else:
            return {
                'id': self.id
            }


class Transaction(object):
    """A Transaction is used to create and transfer assets.

        Note:
            For adding Fulfillments and Conditions, this class provides methods
            to do so.

        Attributes:
            operation (str): Defines the operation of the Transaction.
            fulfillments (:obj:`list` of :class:`~bigchaindb.common.
                transaction.Fulfillment`, optional): Define the assets to
                spend.
            conditions (:obj:`list` of :class:`~bigchaindb.common.
                transaction.Condition`, optional): Define the assets to lock.
            asset (:class:`~.Asset`|:class:`~.AssetLink`): Asset or Asset link
                associated with this Transaction. ``CREATE`` and ``GENESIS``
                Transactions require an Asset while ``TRANSFER`` Transactions
                require an AssetLink.
            metadata (dict):
                Metadata to be stored along with the Transaction.
            version (int): Defines the version number of a Transaction.
    """
    CREATE = 'CREATE'
    TRANSFER = 'TRANSFER'
    GENESIS = 'GENESIS'
    ALLOWED_OPERATIONS = (CREATE, TRANSFER, GENESIS)
    VERSION = 1

    def __init__(self, operation, asset, fulfillments=None, conditions=None,
                 metadata=None, version=None):
        """The constructor allows to create a customizable Transaction.

            Note:
                When no `version` is provided, one is being
                generated by this method.

            Args:
                operation (str): Defines the operation of the Transaction.
                asset (:class:`~.Asset`|:class:`~.AssetLink`): An Asset to be
                    created or an AssetLink linking an asset to be transferred.
                fulfillments (:obj:`list` of :class:`~bigchaindb.common.
                    transaction.Fulfillment`, optional): Define the assets to
                    spend.
                conditions (:obj:`list` of :class:`~bigchaindb.common.
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

        # Assets for 'CREATE' and 'GENESIS' operations must be None or of Asset
        # type and Assets for 'TRANSFER' operations must be of AssetLink type.
        if (operation in [Transaction.CREATE, Transaction.GENESIS] and
                asset is not None and
                not isinstance(asset, Asset)):
            raise TypeError(("`asset` must be an Asset instance for "
                             "'{}' Transactions".format(operation)))
        elif (operation == Transaction.TRANSFER and
                not (asset and isinstance(asset, AssetLink))):
            raise TypeError(("`asset` must be an valid AssetLink instance for "
                             "'TRANSFER' Transactions".format(operation)))

        if conditions and not isinstance(conditions, list):
            raise TypeError('`conditions` must be a list instance or None')

        if fulfillments and not isinstance(fulfillments, list):
            raise TypeError('`fulfillments` must be a list instance or None')

        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError('`metadata` must be a dict or None')

        self.version = version if version is not None else self.VERSION
        self.operation = operation
        self.asset = asset or Asset()
        self.conditions = conditions or []
        self.fulfillments = fulfillments or []
        self.metadata = metadata

        # validate asset
        # we know that each transaction relates to a single asset
        # we can sum the amount of all the conditions
        # for transactions other then CREATE we only have an id so there is
        # nothing we can validate
        if self.operation == self.CREATE:
            amount = sum([condition.amount for condition in self.conditions])
            self.asset.validate_asset(amount=amount)

    @classmethod
    def create(cls, owners_before, owners_after, metadata=None, asset=None):
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
                owners_before (:obj:`list` of :obj:`str`): A list of keys that
                    represent the creators of this asset.
                owners_after (:obj:`list` of :obj:`str`): A list of keys that
                    represent the receivers of this Transaction.
                metadata (dict): Python dictionary to be stored along with the
                    Transaction.
                asset (:class:`~bigchaindb.common.transaction.Asset`): An Asset
                    to be created in this Transaction.

            Returns:
                :class:`~bigchaindb.common.transaction.Transaction`
        """
        if not isinstance(owners_before, list):
            raise TypeError('`owners_before` must be a list instance')
        if not isinstance(owners_after, list):
            raise TypeError('`owners_after` must be a list instance')
        if len(owners_before) == 0:
            raise ValueError('`owners_before` list cannot be empty')
        if len(owners_after) == 0:
            raise ValueError('`owners_after` list cannot be empty')

        fulfillments = []
        conditions = []

        # generate_conditions
        for owner_after in owners_after:
            if not isinstance(owner_after, tuple) or len(owner_after) != 2:
                raise ValueError(('Each `owner_after` in the list must be a'
                                  ' tuple of `([<list of public keys>],'
                                  ' <amount>)`'))
            pub_keys, amount = owner_after
            conditions.append(Condition.generate(pub_keys, amount))

        # generate fulfillments
        fulfillments.append(Fulfillment.generate(owners_before))

        return cls(cls.CREATE, asset, fulfillments, conditions, metadata)

    @classmethod
    def transfer(cls, inputs, owners_after, asset_link, metadata=None):
        """A simple way to generate a `TRANSFER` transaction.

            Note:
                Different cases for threshold conditions:

                Combining multiple `inputs` with an arbitrary number of
                `owners_after` can yield interesting cases for the creation of
                threshold conditions we'd like to support. The following
                notation is proposed:

                1. The index of an `owner_after` corresponds to the index of
                   an input:
                   e.g. `transfer([input1], [a])`, means `input1` would now be
                        owned by user `a`.

                2. `owners_after` can (almost) get arbitrary deeply nested,
                   creating various complex threshold conditions:
                   e.g. `transfer([inp1, inp2], [[a, [b, c]], d])`, means
                        `a`'s signature would have a 50% weight on `inp1`
                        compared to `b` and `c` that share 25% of the leftover
                        weight respectively. `inp2` is owned completely by `d`.

            Args:
                inputs (:obj:`list` of :class:`~bigchaindb.common.transaction.
                    Fulfillment`): Converted "output" Conditions, intended to
                    be used as "input" Fulfillments in the transfer to
                    generate.
                owners_after (:obj:`list` of :obj:`str`): A list of keys that
                    represent the receivers of this Transaction.
                asset_link (:class:`~bigchaindb.common.transaction.AssetLink`):
                    An AssetLink linking an asset to be transferred in this
                    Transaction.
                metadata (dict): Python dictionary to be stored along with the
                    Transaction.

            Returns:
                :class:`~bigchaindb.common.transaction.Transaction`
        """
        if not isinstance(inputs, list):
            raise TypeError('`inputs` must be a list instance')
        if len(inputs) == 0:
            raise ValueError('`inputs` must contain at least one item')
        if not isinstance(owners_after, list):
            raise TypeError('`owners_after` must be a list instance')
        if len(owners_after) == 0:
            raise ValueError('`owners_after` list cannot be empty')

        conditions = []
        for owner_after in owners_after:
            if not isinstance(owner_after, tuple) or len(owner_after) != 2:
                raise ValueError(('Each `owner_after` in the list must be a'
                                  ' tuple of `([<list of public keys>],'
                                  ' <amount>)`'))
            pub_keys, amount = owner_after
            conditions.append(Condition.generate(pub_keys, amount))

        inputs = deepcopy(inputs)
        return cls(cls.TRANSFER, asset_link, inputs, conditions, metadata)

    def __eq__(self, other):
        try:
            other = other.to_dict()
        except AttributeError:
            return False
        return self.to_dict() == other

    def to_inputs(self, condition_indices=None):
        """Converts a Transaction's Conditions to spendable Fulfillments.

            Note:
                Takes the Transaction's Conditions and derives Fulfillments
                from it that can then be passed into `Transaction.transfer` as
                `inputs`.
                A list of integers can be passed to `condition_indices` that
                defines which Conditions should be returned as inputs.
                If no `condition_indices` are passed (empty list or None) all
                Condition of the Transaction are passed.

            Args:
                condition_indices (:obj:`list` of int): Defines which
                    Conditions should be returned as inputs.

            Returns:
                :obj:`list` of :class:`~bigchaindb.common.transaction.
                    Fulfillment`
        """
        # NOTE: If no condition indices are passed, we just assume to
        #       take all conditions as inputs.
        indices = condition_indices or range(len(self.conditions))
        return [
            Fulfillment(self.conditions[cid].fulfillment,
                        self.conditions[cid].owners_after,
                        TransactionLink(self.id, cid))
            for cid in indices
        ]

    def add_fulfillment(self, fulfillment):
        """Adds a Fulfillment to a Transaction's list of Fulfillments.

            Args:
                fulfillment (:class:`~bigchaindb.common.transaction.
                    Fulfillment`): A Fulfillment to be added to the
                    Transaction.
        """
        if not isinstance(fulfillment, Fulfillment):
            raise TypeError('`fulfillment` must be a Fulfillment instance')
        self.fulfillments.append(fulfillment)

    def add_condition(self, condition):
        """Adds a Condition to a Transaction's list of Conditions.

            Args:
                condition (:class:`~bigchaindb.common.transaction.
                    Condition`): A Condition to be added to the
                    Transaction.
        """
        if not isinstance(condition, Condition):
            raise TypeError('`condition` must be a Condition instance or None')
        self.conditions.append(condition)

    def sign(self, private_keys):
        """Fulfills a previous Transaction's Condition by signing Fulfillments.

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

        for index, fulfillment in enumerate(self.fulfillments):
            # NOTE: We clone the current transaction but only add the condition
            #       and fulfillment we're currently working on plus all
            #       previously signed ones.
            tx_partial = Transaction(self.operation, self.asset, [fulfillment],
                                     self.conditions, self.metadata,
                                     self.version)

            tx_partial_dict = tx_partial.to_dict()
            tx_partial_dict = Transaction._remove_signatures(tx_partial_dict)
            tx_serialized = Transaction._to_str(tx_partial_dict)
            self._sign_fulfillment(fulfillment, index, tx_serialized,
                                   key_pairs)
        return self

    def _sign_fulfillment(self, fulfillment, index, tx_serialized, key_pairs):
        """Signs a single Fulfillment with a partial Transaction as message.

            Note:
                This method works only for the following Cryptoconditions
                currently:
                    - Ed25519Fulfillment
                    - ThresholdSha256Fulfillment.

            Args:
                fulfillment (:class:`~bigchaindb.common.transaction.
                    Fulfillment`) The Fulfillment to be signed.
                index (int): The index (or `fid`) of the Fulfillment to be
                    signed.
                tx_serialized (str): The Transaction to be used as message.
                key_pairs (dict): The keys to sign the Transaction with.
        """
        if isinstance(fulfillment.fulfillment, Ed25519Fulfillment):
            self._sign_simple_signature_fulfillment(fulfillment, index,
                                                    tx_serialized, key_pairs)
        elif isinstance(fulfillment.fulfillment, ThresholdSha256Fulfillment):
            self._sign_threshold_signature_fulfillment(fulfillment, index,
                                                       tx_serialized,
                                                       key_pairs)
        else:
            raise ValueError("Fulfillment couldn't be matched to "
                             'Cryptocondition fulfillment type.')

    def _sign_simple_signature_fulfillment(self, fulfillment, index,
                                           tx_serialized, key_pairs):
        """Signs a Ed25519Fulfillment.

            Args:
                fulfillment (:class:`~bigchaindb.common.transaction.
                    Fulfillment`) The Fulfillment to be signed.
                index (int): The index (or `fid`) of the Fulfillment to be
                    signed.
                tx_serialized (str): The Transaction to be used as message.
                key_pairs (dict): The keys to sign the Transaction with.
        """
        # NOTE: To eliminate the dangers of accidentally signing a condition by
        #       reference, we remove the reference of fulfillment here
        #       intentionally. If the user of this class knows how to use it,
        #       this should never happen, but then again, never say never.
        fulfillment = deepcopy(fulfillment)
        owner_before = fulfillment.owners_before[0]
        try:
            # cryptoconditions makes no assumptions of the encoding of the
            # message to sign or verify. It only accepts bytestrings
            fulfillment.fulfillment.sign(tx_serialized.encode(),
                                         key_pairs[owner_before])
        except KeyError:
            raise KeypairMismatchException('Public key {} is not a pair to '
                                           'any of the private keys'
                                           .format(owner_before))
        self.fulfillments[index] = fulfillment

    def _sign_threshold_signature_fulfillment(self, fulfillment, index,
                                              tx_serialized, key_pairs):
        """Signs a ThresholdSha256Fulfillment.

            Args:
                fulfillment (:class:`~bigchaindb.common.transaction.
                    Fulfillment`) The Fulfillment to be signed.
                index (int): The index (or `fid`) of the Fulfillment to be
                    signed.
                tx_serialized (str): The Transaction to be used as message.
                key_pairs (dict): The keys to sign the Transaction with.
        """
        fulfillment = deepcopy(fulfillment)
        for owner_before in fulfillment.owners_before:
            try:
                # TODO: CC should throw a KeypairMismatchException, instead of
                #       our manual mapping here

                # TODO FOR CC: Naming wise this is not so smart,
                #              `get_subcondition` in fact doesn't return a
                #              condition but a fulfillment

                # TODO FOR CC: `get_subcondition` is singular. One would not
                #              expect to get a list back.
                ccffill = fulfillment.fulfillment
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
        self.fulfillments[index] = fulfillment

    def fulfillments_valid(self, input_conditions=None):
        """Validates the Fulfillments in the Transaction against given
        Conditions.

            Note:
                Given a `CREATE` or `GENESIS` Transaction is passed,
                dummyvalues for Conditions are submitted for validation that
                evaluate parts of the validation-checks to `True`.

            Args:
                input_conditions (:obj:`list` of :class:`~bigchaindb.common.
                    transaction.Condition`): A list of Conditions to check the
                    Fulfillments against.

            Returns:
                bool: If all Fulfillments are valid.
        """
        if self.operation in (Transaction.CREATE, Transaction.GENESIS):
            # NOTE: Since in the case of a `CREATE`-transaction we do not have
            #       to check for input_conditions, we're just submitting dummy
            #       values to the actual method. This simplifies it's logic
            #       greatly, as we do not have to check against `None` values.
            return self._fulfillments_valid(['dummyvalue'
                                             for cond in self.fulfillments])
        elif self.operation == Transaction.TRANSFER:
            return self._fulfillments_valid([cond.fulfillment.condition_uri
                                             for cond in input_conditions])
        else:
            allowed_ops = ', '.join(self.__class__.ALLOWED_OPERATIONS)
            raise TypeError('`operation` must be one of {}'
                            .format(allowed_ops))

    def _fulfillments_valid(self, input_condition_uris):
        """Validates a Fulfillment against a given set of Conditions.

            Note:
                The number of `input_condition_uris` must be equal to the
                number of Fulfillments a Transaction has.

            Args:
                input_condition_uris (:obj:`list` of :obj:`str`): A list of
                    Conditions to check the Fulfillments against.

            Returns:
                bool: If all Fulfillments are valid.
        """
        input_condition_uris_count = len(input_condition_uris)
        fulfillments_count = len(self.fulfillments)

        def gen_tx(fulfillment, condition, input_condition_uri=None):
            """Splits multiple IO Transactions into partial single IO
            Transactions.
            """
            tx = Transaction(self.operation, self.asset, [fulfillment],
                             self.conditions, self.metadata, self.version)
            tx_dict = tx.to_dict()
            tx_dict = Transaction._remove_signatures(tx_dict)
            tx_serialized = Transaction._to_str(tx_dict)

            # TODO: Use local reference to class, not `Transaction.`
            return Transaction._fulfillment_valid(fulfillment, self.operation,
                                                  tx_serialized,
                                                  input_condition_uri)

        if not fulfillments_count == input_condition_uris_count:
            raise ValueError('Fulfillments and '
                             'input_condition_uris must have the same count')

        partial_transactions = map(gen_tx, self.fulfillments,
                                   self.conditions, input_condition_uris)
        return all(partial_transactions)

    @staticmethod
    def _fulfillment_valid(fulfillment, operation, tx_serialized,
                           input_condition_uri=None):
        """Validates a single Fulfillment against a single Condition.

            Note:
                In case of a `CREATE` or `GENESIS` Transaction, this method
                does not validate against `input_condition_uri`.

            Args:
                fulfillment (:class:`~bigchaindb.common.transaction.
                    Fulfillment`) The Fulfillment to be signed.
                operation (str): The type of Transaction.
                tx_serialized (str): The Transaction used as a message when
                    initially signing it.
                input_condition_uri (str, optional): A Condition to check the
                    Fulfillment against.

            Returns:
                bool: If the Fulfillment is valid.
        """
        ccffill = fulfillment.fulfillment
        try:
            parsed_ffill = CCFulfillment.from_uri(ccffill.serialize_uri())
        except (TypeError, ValueError, ParsingError):
            return False

        if operation in (Transaction.CREATE, Transaction.GENESIS):
            # NOTE: In the case of a `CREATE` or `GENESIS` transaction, the
            #       input condition is always validate to `True`.
            input_cond_valid = True
        else:
            input_cond_valid = input_condition_uri == ccffill.condition_uri

        # NOTE: We pass a timestamp to `.validate`, as in case of a timeout
        #       condition we'll have to validate against it

        # cryptoconditions makes no assumptions of the encoding of the
        # message to sign or verify. It only accepts bytestrings
        return parsed_ffill.validate(message=tx_serialized.encode(),
                                     now=gen_timestamp()) and input_cond_valid

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Returns:
                dict: The Transaction as an alternative serialization format.
        """
        tx = {
            'fulfillments': [fulfillment.to_dict() for fulfillment
                             in self.fulfillments],
            'conditions': [condition.to_dict() for condition
                           in self.conditions],
            'operation': str(self.operation),
            'metadata': self.metadata,
            'asset': self.asset.to_dict(),
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
        for fulfillment in tx_dict['fulfillments']:
            # NOTE: Not all Cryptoconditions return a `signature` key (e.g.
            #       ThresholdSha256Fulfillment), so setting it to `None` in any
            #       case could yield incorrect signatures. This is why we only
            #       set it to `None` if it's set in the dict.
            fulfillment['fulfillment'] = None
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
        fulfillments = [Fulfillment.from_dict(fulfillment) for fulfillment
                        in tx['fulfillments']]
        conditions = [Condition.from_dict(condition) for condition
                      in tx['conditions']]
        if tx['operation'] in [cls.CREATE, cls.GENESIS]:
            asset = Asset.from_dict(tx['asset'])
        else:
            asset = AssetLink.from_dict(tx['asset'])

        return cls(tx['operation'], asset, fulfillments, conditions,
                   tx['metadata'], tx['version'])
