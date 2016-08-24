from copy import deepcopy
from functools import reduce
from operator import and_
from uuid import uuid4

from cryptoconditions import (
    Fulfillment as CCFulfillment,
    ThresholdSha256Fulfillment,
    Ed25519Fulfillment,
)
from cryptoconditions.exceptions import ParsingError

from bigchaindb_common.crypto import (
    SigningKey,
    hash_data,
)
from bigchaindb_common.exceptions import (
    KeypairMismatchException,
    InvalidHash,
)
from bigchaindb_common.util import (
    serialize,
    gen_timestamp,
)


class Fulfillment(object):
    def __init__(self, fulfillment, owners_before=None, tx_input=None):
        """Create a new fulfillment

        Args:
            # TODO: Write a description here
            owners_before (Optional(list)): base58 encoded public key of the owners of the asset before this
            transaction.
        """
        # TODO: Derive `owner_before` from fulfillment
        self.fulfillment = fulfillment

        if tx_input is not None and not isinstance(tx_input, TransactionLink):
            raise TypeError('`tx_input` must be a TransactionLink instance')
        else:
            self.tx_input = tx_input

        if not isinstance(owners_before, list):
            raise TypeError('`owners_before` must be a list instance')
        else:
            self.owners_before = owners_before

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def to_dict(self):
        try:
            # When we have signed the fulfillment, this will work
            fulfillment = self.fulfillment.serialize_uri()
        except TypeError:
            fulfillment = None

        try:
            # NOTE: `self.tx_input` can be `None` and that's fine
            tx_input = self.tx_input.to_dict()
        except AttributeError:
            tx_input = None

        return {
            'owners_before': self.owners_before,
            'input': tx_input,
            'fulfillment': fulfillment,
            'details': self.fulfillment.to_dict(),
        }

    @classmethod
    def gen_default(cls, owners_after):
        """Creates default fulfillments for transactions, depending on how many `owners_after` are supplied.
        """
        if not isinstance(owners_after, list):
            raise TypeError('`owners_after` must be a list instance')
        else:
            owners_after_count = len(owners_after)

            if owners_after_count == 0:
                # TODO: Replace this error with the logic for a hashlock condition
                raise NotImplementedError('Hashlock conditions are not implemented in BigchainDB yet')
            elif owners_after_count == 1:
                return cls(Ed25519Fulfillment(public_key=owners_after[0]), owners_after)
            else:
                threshold_ffill = cls(ThresholdSha256Fulfillment(threshold=len(owners_after)), owners_after)
                for owner_after in owners_after:
                    threshold_ffill.fulfillment.add_subfulfillment(Ed25519Fulfillment(public_key=owner_after))
                return threshold_ffill

    def gen_condition(self):
        return Condition(self.fulfillment.condition_uri, self.owners_before)

    @classmethod
    def from_dict(cls, ffill):
        """ Serializes a BigchainDB 'jsonized' fulfillment back to a BigchainDB Fulfillment class.
        """
        try:
            fulfillment = CCFulfillment.from_uri(ffill['fulfillment'])
        except TypeError:
            fulfillment = CCFulfillment.from_dict(ffill['details'])
        return cls(fulfillment, ffill['owners_before'], TransactionLink.from_dict(ffill['input']))


class TransactionLink(object):
    # NOTE: In an IPLD implementation, this class is not necessary anymore, as an IPLD link can simply point to an
    #       object, as well as an objects properties. So instead of having a (de)serializable class, we can have a
    #       simple IPLD link of the form: `/<tx_id>/transaction/conditions/<cid>/`
    def __init__(self, txid=None, cid=None):
        self.txid = txid
        self.cid = cid

    def __bool__(self):
        return not (self.txid is None and self.cid is None)

    def __eq__(self, other):
        return self.to_dict() == self.to_dict()

    @classmethod
    def from_dict(cls, link):
        try:
            return cls(link['txid'], link['cid'])
        except TypeError:
            return cls()

    def to_dict(self):
        if self.txid is None and self.cid is None:
            return None
        else:
            return {
                'txid': self.txid,
                'cid': self.cid,
            }


class Condition(object):
    def __init__(self, condition_uri, owners_after=None):
        # TODO: Add more description
        """Create a new condition for a fulfillment

        Args
            owners_after (Optional(list)): base58 encoded public key of the owner of the digital asset after
            this transaction.

        """
        # TODO: Derive `owner_after` from condition
        self.condition_uri = condition_uri

        if not isinstance(owners_after, list):
            raise TypeError('`owners_after` must be a list instance')
        else:
            self.owners_after = owners_after

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def to_dict(self):
        return {
            'owners_after': self.owners_after,
            'condition': self.condition_uri,
        }

    @classmethod
    def from_dict(cls, cond):
        """ Serializes a BigchainDB 'jsonized' condition back to a BigchainDB Condition class.
        """
        return cls(cond['condition'], cond['owners_after'])


class Data(object):
    def __init__(self, payload=None, payload_id=None):
        self.payload_id = payload_id if payload_id is not None else self.to_hash()
        if payload is not None and not isinstance(payload, dict):
            raise TypeError('`payload` must be a dict instance or None')
        else:
            self.payload = payload

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    @classmethod
    def from_dict(cls, payload):
        try:
            return cls(payload['payload'], payload['uuid'])
        except TypeError:
            return cls()

    def to_dict(self):
        if self.payload is None:
            return None
        else:
            return {
                'payload': self.payload,
                'uuid': self.payload_id,
            }

    def to_hash(self):
        return str(uuid4())


class Transaction(object):
    CREATE = 'CREATE'
    TRANSFER = 'TRANSFER'
    GENESIS = 'GENESIS'
    ALLOWED_OPERATIONS = (CREATE, TRANSFER, GENESIS)
    VERSION = 1

    def __init__(self, operation, fulfillments=None, conditions=None, data=None, timestamp=None, version=None):
        # TODO: Update this comment
        """Create a new transaction in memory

        A transaction in BigchainDB is a transfer of a digital asset between two entities represented
        by public keys.

        Currently BigchainDB supports two types of operations:

            `CREATE` - Only federation nodes are allowed to use this operation. In a create operation
            a federation node creates a digital asset in BigchainDB and assigns that asset to a public
            key. The owner of the private key can then decided to transfer this digital asset by using the
            `transaction id` of the transaction as an input in a `TRANSFER` transaction.

            `TRANSFER` - A transfer operation allows for a transfer of the digital assets between entities.

        If a transaction is initialized with the inputs being `None` a `operation` `CREATE` is
        chosen. Otherwise the transaction is of `operation` `TRANSFER`.

        Args:
            # TODO: Write a description here
            fulfillments
            conditions
            operation
           data (Optional[dict]): dictionary with information about asset.

        Raises:
            TypeError: if the optional ``data`` argument is not a ``dict``.

        # TODO: Incorporate this text somewhere better in the docs of this class
        Some use cases for this class:

            1. Create a new `CREATE` transaction:
                - This means `inputs` is empty

            2. Create a new `TRANSFER` transaction:
                - This means `inputs` is a filled list (one to multiple transactions)

            3. Written transactions must be managed somehow in the user's program: use `from_dict`


        """
        self.timestamp = timestamp if timestamp is not None else gen_timestamp()
        self.version = version if version is not None else Transaction.VERSION

        if operation not in Transaction.ALLOWED_OPERATIONS:
            raise TypeError('`operation` must be either CREATE or TRANSFER')
        else:
            self.operation = operation

        if conditions is not None and not isinstance(conditions, list):
            raise TypeError('`conditions` must be a list instance or None')
        elif conditions is None:
            self.conditions = []
        else:
            self.conditions = conditions

        if fulfillments is not None and not isinstance(fulfillments, list):
            raise TypeError('`fulfillments` must be a list instance or None')
        elif fulfillments is None:
            self.fulfillments = []
        else:
            self.fulfillments = fulfillments

        if data is not None and not isinstance(data, Data):
            raise TypeError('`data` must be a Data instance or None')
        else:
            self.data = data

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    @classmethod
    def create(cls, owners_before, owners_after, inputs, operation, payload=None):
        if operation == Transaction.CREATE or operation == Transaction.GENESIS:
            ffill = Fulfillment.gen_default(owners_after)
            cond = ffill.gen_condition()
            return cls(operation, [ffill], [cond], Data(payload))
        else:
            # TODO: Replace this with an actual implementation, maybe calling
            #       `self.transfer` is sufficient already :)
            raise NotImplementedError()

    def transfer(self, conditions):
        # TODO: Check here if a condition is submitted or smth else
        return self.__class__(Transaction.TRANSFER, self._fulfillments_as_inputs(), conditions)

    def simple_transfer(self, owners_after):
        condition = Fulfillment.gen_default(owners_after).gen_condition()
        return self.transfer([condition])

    def _fulfillments_as_inputs(self):
        return [Fulfillment(ffill.fulfillment,
                            ffill.owners_before,
                            TransactionLink(self.to_hash(), fulfillment_id))
                for fulfillment_id, ffill in enumerate(self.fulfillments)]

    def add_fulfillment(self, fulfillment):
        if fulfillment is not None and not isinstance(fulfillment, Fulfillment):
            raise TypeError('`fulfillment` must be a Fulfillment instance or None')
        else:
            self.fulfillments.append(fulfillment)

    def add_condition(self, condition):
        if condition is not None and not isinstance(condition, Condition):
            raise TypeError('`condition` must be a Condition instance or None')
        else:
            self.conditions.append(condition)

    # TODO: This shouldn't be in the base of the Transaction class, but rather only for the client implementation,
    #       since for example the Transaction class in BigchainDB doesn't have to sign transactions.
    def sign(self, private_keys):
        """ Signs a transaction
            Acts as a proxy for `_sign_fulfillments`, for exposing a nicer API to the outside.
        """
        self._sign_fulfillments(private_keys)
        return self

    # TODO: This shouldn't be in the base of the Transaction class, but rather only for the client implementation,
    #       since for example the Transaction class in BigchainDB doesn't have to sign transactions.
    def _sign_fulfillments(self, private_keys):
        if private_keys is None or not isinstance(private_keys, list):
            raise TypeError('`private_keys` must be a list instance')

        # Generate public keys from private keys and match them in a dictionary:
        #   key:     public_key
        #   value:   private_key
        def gen_public_key(private_key):
            # TODO FOR CC: Adjust interface so that this function becomes unnecessary
            return private_key.get_verifying_key().to_ascii().decode()
        key_pairs = {gen_public_key(SigningKey(private_key)): SigningKey(private_key) for private_key in private_keys}

        # TODO: The condition for a transfer-tx will come from an input
        for fulfillment, condition in zip(self.fulfillments, self.conditions):
            # NOTE: We clone the current transaction but only add the condition and fulfillment we're currently
            # working on plus all previously signed ones.
            tx_partial = Transaction(self.operation, [fulfillment], [condition], self.data, self.timestamp,
                                     self.version)
            tx_serialized = Transaction._to_str(Transaction._remove_signatures(tx_partial.to_dict()))
            self._sign_fulfillment(fulfillment, tx_serialized, key_pairs)

    # TODO: This shouldn't be in the base of the Transaction class, but rather only for the client implementation,
    #       since for example the Transaction class in BigchainDB doesn't have to sign transactions.
    def _sign_fulfillment(self, fulfillment, tx_serialized, key_pairs):
        if isinstance(fulfillment.fulfillment, Ed25519Fulfillment):
            self._sign_simple_signature_fulfillment(fulfillment, tx_serialized, key_pairs)
        elif isinstance(fulfillment.fulfillment, ThresholdSha256Fulfillment):
            self._sign_threshold_signature_fulfillment(fulfillment, tx_serialized, key_pairs)

    # TODO: This shouldn't be in the base of the Transaction class, but rather only for the client implementation,
    #       since for example the Transaction class in BigchainDB doesn't have to sign transactions.
    def _sign_simple_signature_fulfillment(self, fulfillment, tx_serialized, key_pairs):
        # TODO: Update comment
        """Fulfill a cryptoconditions.Ed25519Fulfillment

            Args:
                fulfillment (dict): BigchainDB fulfillment to fulfill.
                parsed_fulfillment (cryptoconditions.Ed25519Fulfillment): cryptoconditions.Ed25519Fulfillment instance.
                fulfillment_message (dict): message to sign.
                key_pairs (dict): dictionary of (public_key, private_key) pairs.

            Returns:
                object: fulfilled cryptoconditions.Ed25519Fulfillment

        """
        owner_before = fulfillment.owners_before[0]
        try:
            # NOTE: By signing the CC fulfillment here directly, we're changing the transactions's fulfillment by
            # reference, and that's good :)
            fulfillment.fulfillment.sign(tx_serialized, key_pairs[owner_before])
        except KeyError:
            raise KeypairMismatchException('Public key {} is not a pair to any of the private keys'
                                           .format(owner_before))

    # TODO: This shouldn't be in the base of the Transaction class, but rather only for the client implementation,
    #       since for example the Transaction class in BigchainDB doesn't have to sign transactions.
    def _sign_threshold_signature_fulfillment(self, fulfillment, tx_serialized, key_pairs):
        # TODO: Update comment
        """Fulfill a cryptoconditions.ThresholdSha256Fulfillment

            Args:
                fulfillment (dict): BigchainDB fulfillment to fulfill.
                parsed_fulfillment (ThresholdSha256Fulfillment): ThresholdSha256Fulfillment instance.
                fulfillment_message (dict): message to sign.
                key_pairs (dict): dictionary of (public_key, private_key) pairs.

            Returns:
                object: fulfilled cryptoconditions.ThresholdSha256Fulfillment

        """
        for owner_before in fulfillment.owners_before:
            try:
                # TODO: CC should throw a KeypairMismatchException, instead of our manual mapping here
                # TODO FOR CC: Naming wise this is not so smart, `get_subcondition` in fact doesn't return a condition
                #              but a fulfillment:(
                # TODO FOR CC: `get_subcondition` is singular. One would not expect to get a list back.
                subfulfillment = fulfillment.fulfillment.get_subcondition_from_vk(owner_before)[0]
            except IndexError:
                raise KeypairMismatchException('Public key {} cannot be found in the fulfillment'
                                               .format(owner_before))
            try:
                private_key = key_pairs[owner_before]
            except KeyError:
                raise KeypairMismatchException('Public key {} is not a pair to any of the private keys'
                                               .format(owner_before))

            subfulfillment.sign(tx_serialized, private_key)

    def fulfillments_valid(self, input_conditions=None):
        if isinstance(input_conditions, list):
            return self._fulfillments_valid([cond.condition_uri for cond
                                            in input_conditions])
        elif input_conditions is None:
            return self._fulfillments_valid()
        else:
            raise TypeError('`input_conditions` must be list instance or None')

    def _fulfillments_valid(self, input_condition_uris=None):
        # TODO: Update Comment
        if input_condition_uris is None:
            input_condition_uris = []

        input_condition_uris_count = len(input_condition_uris)
        fulfillments_count = len(self.fulfillments)
        conditions_count = len(self.conditions)

        def gen_tx(fulfillment, condition, input_condition_uri=None):
            tx = Transaction(self.operation, [fulfillment], [condition], self.data, self.timestamp, self.version)
            if input_condition_uri is not None:
                return tx._fulfillments_valid([input_condition_uri])
            else:
                return tx._fulfillments_valid()

        if self.operation in (Transaction.CREATE, Transaction.GENESIS):
            if not fulfillments_count == conditions_count:
                raise ValueError('Fulfillments, conditions must have the same count')
            elif fulfillments_count > 1 and conditions_count > 1:
                return reduce(and_, map(gen_tx, self.fulfillments, self.conditions))
            else:
                return self._fulfillment_valid()
        elif self.operation is Transaction.TRANSFER:
            if not fulfillments_count == conditions_count == input_condition_uris_count:
                raise ValueError('Fulfillments, conditions and input_condition_uris must have the same count')
            elif fulfillments_count > 1 and conditions_count > 1 and input_condition_uris_count > 1:
                return reduce(and_, map(gen_tx, self.fulfillments, self.conditions, input_condition_uris))
            else:
                return self._fulfillment_valid(input_condition_uris.pop())
        else:
            raise TypeError('`operation` must be either `TRANSFER`, `CREATE` or `GENESIS`')

    def _fulfillment_valid(self, input_condition_uri=None):
        # NOTE: We're always taking the first fulfillment, as this method is called recursively.
        #       See: `fulfillments_valid`
        fulfillment = self.fulfillments[0]

        try:
            parsed_fulfillment = CCFulfillment.from_uri(fulfillment.fulfillment.serialize_uri())
        except (TypeError, ValueError, ParsingError):
            return False

        if self.operation == Transaction.CREATE:
            input_condition_valid = True
        else:
            # NOTE: When passing a `TRANSFER` transaction for validation, we check if it's valid by validating its
            #       input condition (taken from previous transaction) against the current fulfillment.
            input_condition_valid = input_condition_uri == fulfillment.fulfillment.condition_uri

        tx_serialized = Transaction._to_str(Transaction._remove_signatures(self.to_dict()))
        # NOTE: We pass a timestamp to `.validate`, as in case of a timeout condition we'll have to validate against
        #       it.
        return parsed_fulfillment.validate(message=tx_serialized, now=gen_timestamp()) and input_condition_valid

    def to_dict(self):
        try:
            data = self.data.to_dict()
        except AttributeError:
            # NOTE: data can be None and that's OK
            data = None

        tx_body = {
            'fulfillments': [fulfillment.to_dict() for fulfillment in self.fulfillments],
            'conditions': [condition.to_dict() for condition in self.conditions],
            'operation': str(self.operation),
            'timestamp': self.timestamp,
            'data': data,
        }
        tx = {
            'version': self.version,
            'transaction': tx_body,
        }

        tx_id = Transaction._to_hash(Transaction._to_str(Transaction._remove_signatures(tx)))
        tx['id'] = tx_id

        return tx

    @staticmethod
    def _remove_signatures(tx_dict):
        # NOTE: We remove the reference since we need `tx_dict` only for the transaction's hash
        tx_dict = deepcopy(tx_dict)
        for fulfillment in tx_dict['transaction']['fulfillments']:
            # NOTE: Not all Cryptoconditions return a `signature` key (e.g. ThresholdSha256Fulfillment), so setting it
            #       to `None` in any case could yield incorrect signatures. This is why we only set it to `None` if
            #       it's set in the dict.
            if 'signature' in fulfillment['details']:
                fulfillment['details']['signature'] = None
            fulfillment['fulfillment'] = None
            try:
                for subfulfillment in fulfillment['details']['subfulfillments']:
                    subfulfillment['signature'] = None
            except KeyError:
                pass
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

    def __str__(self):
        return Transaction._to_str(self.to_dict())

    @classmethod
    # TODO: Make this method more pretty
    def from_dict(cls, tx_body):
        # NOTE: Remove reference to avoid side effects
        tx_body = deepcopy(tx_body)
        try:
            proposed_tx_id = tx_body.pop('id')
        except KeyError:
            raise InvalidHash()
        valid_tx_id = Transaction._to_hash(Transaction._to_str(Transaction._remove_signatures(tx_body)))
        if proposed_tx_id != valid_tx_id:
            raise InvalidHash()
        else:
            tx = tx_body['transaction']
            fulfillments = [Fulfillment.from_dict(fulfillment) for fulfillment
                            in tx['fulfillments']]
            conditions = [Condition.from_dict(condition) for condition
                          in tx['conditions']]
            data = Data.from_dict(tx['data'])
            return cls(tx['operation'], fulfillments, conditions, data,
                       tx['timestamp'], tx_body['version'])
