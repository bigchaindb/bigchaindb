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

# TODO: Eventually remove all coupling from the core BigchainDB code base, as this module will life separately.
from bigchaindb_common.crypto import (
    SigningKey,
    hash_data,
)
from bigchaindb_common.exceptions import (
    KeypairMismatchException,
)
from bigchaindb_common.util import (
    serialize,
    gen_timestamp,
)


class Fulfillment(object):
    def __init__(self, fulfillment, owners_before=None, fid=0, tx_input=None):
        """Create a new fulfillment

        Args:
            # TODO: Write a description here
            owners_before (Optional(list)): base58 encoded public key of the owners of the asset before this
            transaction.
        """
        self.fid = fid
        # TODO: Check if `fulfillment` corresponds to `owners_before`, otherwise fail
        self.fulfillment = fulfillment

        if tx_input is not None and not isinstance(tx_input, TransactionLink):
            raise TypeError('`tx_input` must be a TransactionLink instance')
        else:
            self.tx_input = tx_input

        if not isinstance(owners_before, list):
            raise TypeError('`owners_before` must be a list instance')
        else:
            self.owners_before = owners_before

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
            'fid': self.fid,
        }

    @classmethod
    def gen_default(cls, owners_after, fid=0):
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
                return cls(Ed25519Fulfillment(public_key=owners_after[0]), owners_after, fid)
            else:
                threshold_ffill = cls(ThresholdSha256Fulfillment(threshold=len(owners_after)), owners_after, fid)
                for owner_after in owners_after:
                    threshold_ffill.fulfillment.add_subfulfillment(Ed25519Fulfillment(public_key=owner_after))
                return threshold_ffill

    def gen_condition(self):
        return Condition(self.fulfillment.condition_uri, self.owners_before, self.fid)

    @classmethod
    def from_dict(cls, ffill):
        """ Serializes a BigchainDB 'jsonized' fulfillment back to a BigchainDB Fulfillment class.
        """
        try:
            fulfillment = CCFulfillment.from_uri(ffill['fulfillment'])
        except TypeError:
            fulfillment = CCFulfillment.from_dict(ffill['details'])
        return cls(fulfillment, ffill['owners_before'], ffill['fid'], TransactionLink.from_dict(ffill['input']))


class Condition(object):
    def __init__(self, condition_uri, owners_after=None, cid=0):
        # TODO: Add more description
        """Create a new condition for a fulfillment

        Args
            owners_after (Optional(list)): base58 encoded public key of the owner of the digital asset after
            this transaction.

        """
        self.cid = cid
        # TODO: Check if `condition_uri` corresponds to `owners_after`, otherwise fail
        self.condition_uri = condition_uri

        if not isinstance(owners_after, list):
            raise TypeError('`owners_after` must be a list instance')
        else:
            self.owners_after = owners_after

    def to_dict(self):
        return {
            'owners_after': self.owners_after,
            'condition': self.condition_uri,
            'cid': self.cid
        }

    @classmethod
    def from_dict(cls, cond):
        """ Serializes a BigchainDB 'jsonized' condition back to a BigchainDB Condition class.
        """
        return cls(cond['condition'], cond['owners_after'], cond['cid'])


class Data(object):
    def __init__(self, payload=None, payload_id=None):
        self.payload_id = payload_id if payload_id is not None else self.to_hash()
        if payload is not None and not isinstance(payload, dict):
            raise TypeError('`payload` must be a dict instance or None')
        else:
            self.payload = payload

    @classmethod
    def from_dict(cls, payload):
        try:
            return cls(payload['payload'], payload['hash'])
        except TypeError:
            return cls()

    def to_dict(self):
        if self.payload is None:
            return None
        else:
            return {
                'payload': self.payload,
                'hash': str(self.payload_id),
            }

    def to_hash(self):
        return uuid4()


class TransactionLink(object):
    # NOTE: In an IPLD implementation, this class is not necessary anymore, as an IPLD link can simply point to an
    #       object, as well as an objects properties. So instead of having a (de)serializable class, we can have a
    #       simple IPLD link of the form (not clear yet how to address indexes in arrays:
    #        - https://github.com/ipld/specs/issues/20
    def __init__(self, tx_id=None, cid=None):
        self.tx_id = tx_id
        self.cid = cid

    @classmethod
    def from_dict(cls, link):
        try:
            return cls(link['tx_id'], link['cid'])
        except TypeError:
            return cls()

    def to_dict(self):
        if self.tx_id is None and self.cid is None:
            return None
        else:
            return {
                'tx_id': self.tx_id,
                'cid': self.cid,
            }


class Transaction(object):
    CREATE = 'CREATE'
    TRANSFER = 'TRANSFER'
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

        if operation is not Transaction.CREATE and operation is not Transaction.TRANSFER:
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

        # TODO: rename this to data
        if data is not None and not isinstance(data, Data):
            raise TypeError('`data` must be a Data instance or None')
        else:
            self.data = data

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
        if private_keys is None:
            # TODO: Figure out the correct Python error
            raise Exception('`private_keys` cannot be None')
        if not isinstance(private_keys, list):
            private_keys = [private_keys]

        # Generate public keys from private keys and match them in a dictionary:
        #   key:     public_key
        #   value:   private_key
        gen_public_key = lambda private_key: private_key.get_verifying_key().to_ascii().decode()
        key_pairs = {gen_public_key(SigningKey(private_key)): SigningKey(private_key) for private_key in private_keys}

        # TODO: The condition for a transfer-tx will come from an input
        for fulfillment, condition in zip(self.fulfillments, self.conditions):
            # NOTE: We clone the current transaction but only add the condition and fulfillment we're currently
            # working on.
            tx_partial = Transaction(self.operation, [fulfillment], [condition], self.data, self.timestamp,
                                     self.version)
            self._sign_fulfillment(fulfillment, str(tx_partial), key_pairs)

    # TODO: This shouldn't be in the base of the Transaction class, but rather only for the client implementation,
    #       since for example the Transaction class in BigchainDB doesn't have to sign transactions.
    def _sign_fulfillment(self, fulfillment, tx_serialized, key_pairs):
        if isinstance(fulfillment.fulfillment, Ed25519Fulfillment):
            self._fulfill_simple_signature_fulfillment(fulfillment, tx_serialized, key_pairs)
        elif isinstance(fulfillment.fulfillment, ThresholdSha256Fulfillment):
            self._fulfill_threshold_signature_fulfillment(fulfillment, tx_serialized, key_pairs)

    # TODO: This shouldn't be in the base of the Transaction class, but rather only for the client implementation,
    #       since for example the Transaction class in BigchainDB doesn't have to sign transactions.
    def _fulfill_simple_signature_fulfillment(self, fulfillment, tx_serialized, key_pairs):
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
    def _fulfill_threshold_signature_fulfillment(self, fulfillment, tx_serialized, key_pairs):
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

    def fulfillments_valid(self):
        # TODO: Update Comment
        """Verify the signature of a transaction

        A valid transaction should have been signed `current_owner` corresponding private key.

        Args:
            signed_transaction (dict): a transaction with the `signature` included.

        Returns:
            bool: True if the signature is correct, False otherwise.
        """
        zipped_io = list(zip(self.fulfillments, self.conditions))

        if len(zipped_io) > 1:
            # TODO: The condition for a transfer-tx will come from an input
            gen_tx = lambda ffill, cond: Transaction(self.operation, [ffill], [cond], self.data, self.timestamp,
                                                     self.version).fulfillments_valid()
            return reduce(and_, map(gen_tx, zipped_io))
        else:
            return self._fulfillment_valid()

    def _fulfillment_valid(self):
        # NOTE: We're always taking the first fulfillment, as this method is called recursively.
        #       See: `fulfillments_valid`
        fulfillment = self.fulfillments[0].fulfillment

        try:
            parsed_fulfillment = CCFulfillment.from_uri(fulfillment.serialize_uri())
        # TODO: Figure out if we need all three of those errors here
        except (TypeError, ValueError, ParsingError):
            return False

        # TODO: For transfer-transaction, we'll also have to validate against the given condition
        # NOTE: We pass a timestamp here, as in case of a timeout condition we'll have to validate against it.
        return parsed_fulfillment.validate(message=Transaction._to_str(Transaction._remove_signatures(self.to_dict())),
                                           now=gen_timestamp())

    def transfer(self, conditions):
        return Transaction(Transaction.TRANSFER, self._fulfillments_as_inputs(), conditions)

    def _fulfillments_as_inputs(self):
        return [Fulfillment(ffill.fulfillment,
                            ffill.owners_before,
                            ffill.fid,
                            TransactionLink(self.to_hash(), ffill.fid))
                for ffill in self.fulfillments]

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
        # NOTE: Remove reference since we need `tx_dict` only for the transaction's hash
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

    def to_hash(self):
        return self.to_dict()['id']

    @staticmethod
    def _to_str(value):
        return serialize(value)

    def __str__(self):
        return Transaction._to_str(self.to_dict())

    @classmethod
    def from_dict(cls, tx_body):
        tx = tx_body['transaction']
        return cls(tx['operation'], [Fulfillment.from_dict(fulfillment) for fulfillment in tx['fulfillments']],
                   [Condition.from_dict(condition) for condition in tx['conditions']], Data.from_dict(tx['data']),
                   tx['timestamp'], tx_body['version'])
