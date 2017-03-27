from copy import deepcopy
from collections import namedtuple

from bigchaindb.common.crypto import hash_data
from bigchaindb.common.exceptions import (InvalidHash, AmountError,
                                          AssetIdMismatch, ValidationError,
                                          InvalidSignature)
from bigchaindb_shared import BDBError, call_json_rpc
from bigchaindb.common.utils import serialize
import bigchaindb.version


class Input(namedtuple('_', 'fulfillment,fulfills')):
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

    def __new__(self, fulfillment, fulfills=None):
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

        return super().__new__(self, fulfillment, fulfills)

    def __eq__(self, other):
        # TODO: If `other !== Fulfillment` return `False`
        return self.to_dict() == other.to_dict()

    @property
    def condition(self):
        if isinstance(self.fulfillment, dict):
            return self.fulfillment
        return call_shared('readFulfillment', {
            'fulfillment': self.fulfillment,
        })

    def sign(self, private_keys, msg):
        request = {
            'condition': self.condition,
            'keys': private_keys,
            'msg': msg
        }
        out = call_shared('signCondition', request)
        return self._replace(fulfillment=out)

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Note:
                If an Input hasn't been signed yet, this method returns a
                dictionary representation.

            Returns:
                dict: The Input as an alternative serialization format.
        """

        input_ = {
            'fulfillment': self.fulfillment,
        }
        if self.fulfills:
            input_['fulfills'] = self.fulfills.to_dict()
        return input_

    @classmethod
    def generate(cls, public_keys):
        return cls(generate_condition(public_keys))

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
        fulfills = None
        if 'fulfills' in data:
            fulfills = TransactionLink.from_dict(data['fulfills'])
        return cls(data['fulfillment'], fulfills)


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

    @classmethod
    def from_dict(cls, link):
        """Transforms a Python dictionary to a TransactionLink object.

            Args:
                link (dict): The link to be transformed.

            Returns:
                :class:`~bigchaindb.common.transaction.TransactionLink`
        """
        try:
            return cls(link['txid'], link['output'])
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
                'txid': self.txid,
                'output': self.output,
            }

    def to_uri(self, path=''):
        if self.txid is None and self.output is None:
            return None
        return '{}/transactions/{}/outputs/{}'.format(path, self.txid,
                                                      self.output)


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
            asset (dict): Asset payload for this Transaction. ``CREATE`` and
                ``GENESIS`` Transactions require a dict with a ``data``
                property while ``TRANSFER`` Transactions require a dict with a
                ``id`` property.
            metadata (dict):
                Metadata to be stored along with the Transaction.
            version (int): Defines the version number of a Transaction.
    """
    CREATE = 'CREATE'
    TRANSFER = 'TRANSFER'
    GENESIS = 'GENESIS'
    ALLOWED_OPERATIONS = (CREATE, TRANSFER, GENESIS)
    VERSION = '.'.join(bigchaindb.version.__short_version__.split('.')[:2])

    def __init__(self, operation, asset, inputs=None, outputs=None,
                 metadata=None, version=None):
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
                version (int): Defines the version number of a Transaction.
        """
        if operation not in Transaction.ALLOWED_OPERATIONS:
            allowed_ops = ', '.join(self.__class__.ALLOWED_OPERATIONS)
            raise ValueError('`operation` must be one of {}'
                             .format(allowed_ops))

        # Asset payloads for 'CREATE' and 'GENESIS' operations must be None or
        # dicts holding a `data` property. Asset payloads for 'TRANSFER'
        # operations must be dicts holding an `id` property.
        if (operation in [Transaction.CREATE, Transaction.GENESIS] and
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
            Input(self.outputs[idx].condition,
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

        for i, input_ in enumerate(self.inputs):
            msg = '%s:%s' % (i, str(self))
            self.inputs[i] = input_.sign(private_keys, msg)
        return self

    def inputs_valid(self, outputs=None):
        def verify(i, condition):
            fulfillment = self.inputs[i].fulfillment
            if type(fulfillment) == dict:
                return False
            request = {
                'msg': ('%s:%s' % (i, str(self))),
                'fulfillment': self.inputs[i].fulfillment,
                'condition': condition
            }
            out = call_shared('verifyFulfillment', request)
            return out['valid']

        if self.operation == Transaction.TRANSFER:
            for i, input_ in enumerate(self.inputs):
                if not verify(i, outputs[i].condition):
                    return False
            return True
        else:
            ffill = self.inputs[0].fulfillment
            if not isinstance(ffill, str):
                return False
            try:
                call_shared('readFulfillment', {
                    'fulfillment': ffill
                })
            except InvalidSignature:
                return False
            return True

    def to_dict(self):
        """Transforms the object to a Python dictionary.

            Returns:
                dict: The Transaction as an alternative serialization format.
        """
        tx = {
            'inputs': [input_.to_dict() for input_ in self.inputs],
            'outputs': [output.to_dict() for output in self.outputs],
            'operation': str(self.operation),
            'metadata': self.metadata,
            'asset': self.asset,
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
        for input_ in tx_dict['inputs']:
            # NOTE: Not all Cryptoconditions return a `signature` key (e.g.
            #       ThresholdSha256Fulfillment), so setting it to `None` in any
            #       case could yield incorrect signatures. This is why we only
            #       set it to `None` if it's set in the dict.
            input_['fulfillment'] = None
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
        cls.validate_id(tx)
        inputs = [Input.from_dict(input_) for input_ in tx['inputs']]
        outputs = [Output.from_dict(output) for output in tx['outputs']]
        return cls(tx['operation'], tx['asset'], inputs, outputs,
                   tx['metadata'], tx['version'])


def generate_condition(public_keys):
    if not isinstance(public_keys, list):
        raise TypeError('`public_keys` must be an instance of list')
    if not all(map(lambda pk: isinstance(pk, str), public_keys)):
        raise ValueError('`public_keys` items must all be str')
    if len(public_keys) == 0:
        raise ValueError('`public_keys` needs to contain at least one'
                         'owner')
    if len(public_keys) == 1 and not isinstance(public_keys[0], list):
        expr = public_keys[0]
    else:
        expr = '(%s of %s)' % (len(public_keys), ','.join(public_keys))
    return call_shared('parseConditionDSL', {'expr': expr})


class Output(namedtuple('_', 'condition,amount')):
    def __new__(self, condition, amount):
        if not isinstance(amount, int):
            raise TypeError('`amount` must be a int')
        if amount < 1:
            raise AmountError('`amount` needs to be greater than zero')
        return super().__new__(self, condition, amount)

    @classmethod
    def generate(cls, public_keys, amount):
        condition = generate_condition(public_keys)
        return Output(condition, amount)

    @classmethod
    def from_dict(cls, data):
        return cls(data['condition'], int(data['amount']))

    def to_dict(self):
        return {
            'amount': self.amount,
            'condition': self.condition,
        }


def call_shared(method, params):
    exception_map = {
        100: ValidationError,
        102: InvalidSignature,
        -32601: AttributeError,  # Method not found
        -32602: ValueError,  # Invalid Params
    }
    try:
        return call_json_rpc(method, params)
    except BDBError as e:
        raise exception_map[e.args[0]](*e.args[1:]) from e
