from copy import deepcopy
from functools import reduce
from operator import and_
from uuid import uuid4

from cryptoconditions import (Fulfillment as CCFulfillment,
                              ThresholdSha256Fulfillment, Ed25519Fulfillment,
                              PreimageSha256Fulfillment)
from cryptoconditions.exceptions import ParsingError

from bigchaindb_common.crypto import SigningKey, hash_data
from bigchaindb_common.exceptions import (KeypairMismatchException,
                                          InvalidHash, InvalidSignature)
from bigchaindb_common.util import serialize, gen_timestamp


class Fulfillment(object):
    def __init__(self, fulfillment, owners_before, tx_input=None):
        self.fulfillment = fulfillment

        if tx_input is not None and not isinstance(tx_input, TransactionLink):
            raise TypeError('`tx_input` must be a TransactionLink instance')
        else:
            self.tx_input = tx_input

        if not isinstance(owners_before, list):
            raise TypeError('`owners_after` must be a list instance')
        else:
            self.owners_before = owners_before

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def to_dict(self, fid=None):
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
        if fid is not None:
            ffill['fid'] = fid
        return ffill

    @classmethod
    def from_dict(cls, ffill):
        """ Serializes a BigchainDB 'jsonized' fulfillment back to a BigchainDB Fulfillment class.
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
        return cls(fulfillment, ffill['owners_before'], TransactionLink.from_dict(ffill['input']))


class TransactionLink(object):
    # NOTE: In an IPLD implementation, this class is not necessary anymore,
    # as an IPLD link can simply point to an object, as well as an objects
    # properties. So instead of having a (de)serializable class, we can have a
    # simple IPLD link of the form: `/<tx_id>/transaction/conditions/<cid>/`
    def __init__(self, txid=None, cid=None):
        self.txid = txid
        self.cid = cid

    def __bool__(self):
        return self.txid is not None and self.cid is not None

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
    def __init__(self, fulfillment, owners_after=None):
        # TODO: Add more description
        self.fulfillment = fulfillment

        if not isinstance(owners_after, list) and owners_after is not None:
            raise TypeError('`owners_after` must be a list instance or None')
        else:
            self.owners_after = owners_after

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def to_dict(self, cid=None):
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
            'condition': condition
        }
        if cid is not None:
            cond['cid'] = cid
        return cond

    @classmethod
    def generate(cls, owners_after):
        """Generates conditions from a specifically formed tuple or list.

            If a ThresholdCondition has to be generated where the threshold is
            always the number of subconditions it is split between, a list of
            the following structure is sufficient:

            [(address|condition)*, [(address|condition)*, ...], ...]

            If however, the thresholds of individual threshold conditions to be
            created have to be set specifically, a tuple of the following
            structure is necessary:

            ([(address|condition)*,
              ([(address|condition)*, ...], subthreshold),
              ...], threshold)

            Args:
                owners_after (list|tuple): The users that should be able to
                                           fulfill the condition that is being
                                           created.
            Returns:
                A `Condition` that can be used in a `Transaction`.

        """
        if isinstance(owners_after, tuple):
            owners_after, threshold = owners_after
        else:
            threshold = len(owners_after)

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
            return cls(ffill, owners_after)
        else:
            initial_cond = ThresholdSha256Fulfillment(threshold=threshold)
            threshold_cond = reduce(cls._gen_condition, owners_after,
                                    initial_cond)
            return cls(threshold_cond, owners_after)

    @classmethod
    def _gen_condition(cls, initial, current):
        if isinstance(current, tuple):
            owners_after, threshold = current
        else:
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
        try:
            fulfillment = CCFulfillment.from_dict(cond['condition']['details'])
        except KeyError:
            # NOTE: Hashlock condition case
            fulfillment = cond['condition']['uri']
        return cls(fulfillment, cond['owners_after'])


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

    def __init__(self, operation, fulfillments=None, conditions=None,
                 data=None, timestamp=None, version=None):
        # TODO: Write a comment
        self.timestamp = timestamp if timestamp is not None else gen_timestamp()
        self.version = version if version is not None else Transaction.VERSION

        if operation not in Transaction.ALLOWED_OPERATIONS:
            raise TypeError('`operation` must be one of {}'
                            .format(', '.join(self.__class__.ALLOWED_OPERATIONS)))
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

    @classmethod
    def create(cls, owners_before, owners_after, payload=None, secret=None,
               time_expire=None):
        if not isinstance(owners_before, list):
            raise TypeError('`owners_before` must be a list instance')
        if not isinstance(owners_after, list):
            raise TypeError('`owners_after` must be a list instance')

        data = Data(payload)
        if len(owners_before) == len(owners_after) and len(owners_after) == 1:
            # NOTE: Standard case, one owner before, one after.
            # NOTE: For this case its sufficient to use the same
            #       fulfillment for the fulfillment and condition.
            ffill = Ed25519Fulfillment(public_key=owners_before[0])
            ffill_tx = Fulfillment(ffill, owners_before)
            cond_tx = Condition.generate(owners_after)
            return cls(cls.CREATE, [ffill_tx], [cond_tx], data)

        elif len(owners_before) == len(owners_after) and len(owners_after) > 1:
            raise NotImplementedError('Multiple inputs and outputs not'
                                      'available for CREATE')
            # NOTE: Multiple inputs and outputs case. Currently not supported.
            ffills = [Fulfillment(Ed25519Fulfillment(public_key=owner_before),
                                  [owner_before])
                      for owner_before in owners_before]
            conds = [Condition.generate(owners) for owners in owners_after]
            return cls(cls.CREATE, ffills, conds, data)

        elif len(owners_before) == 1 and len(owners_after) > 1:
            # NOTE: Multiple owners case
            cond_tx = Condition.generate(owners_after)
            ffill = Ed25519Fulfillment(public_key=owners_before[0])
            ffill_tx = Fulfillment(ffill, owners_before)
            return cls(cls.CREATE, [ffill_tx], [cond_tx], data)

        elif len(owners_before) == 1 and len(owners_after) == 0 and secret is not None:
            # NOTE: Hashlock condition case
            hashlock = PreimageSha256Fulfillment(preimage=secret)
            cond_tx = Condition(hashlock.condition_uri)
            ffill = Ed25519Fulfillment(public_key=owners_before[0])
            ffill_tx = Fulfillment(ffill, owners_before)
            return cls(cls.CREATE, [ffill_tx], [cond_tx], data)

        elif len(owners_before) > 0 and len(owners_after) == 0 and time_expire is not None:
            raise NotImplementedError('Timeout conditions will be implemented later')

        elif len(owners_before) > 0 and len(owners_after) == 0 and secret is None:
            raise ValueError('Define a secret to create a hashlock condition')

        else:
            raise ValueError("These are not the cases you're looking for ;)")

    @classmethod
    def transfer(cls, inputs, owners_after, payload=None):
        if not isinstance(inputs, list):
            raise TypeError('`inputs` must be a list instance')
        if len(inputs) == 0:
            raise ValueError('`inputs` must contain at least one item')
        if not isinstance(owners_after, list):
            raise TypeError('`owners_after` must be a list instance')

        # NOTE: Different cases for threshold conditions:
        #
        #       Combining multiple `inputs` with an arbitrary number of
        #       `owners_after` can yield interesting cases for the creation of
        #       threshold conditions we'd like to support. The following
        #       notation is proposed:
        #
        #       1. The index of an `owner_after` corresponds to the index of
        #          an input:
        #          e.g. `transfer([input1], [a])`, means `input1` would now be
        #               owned by user `a`.
        #
        #       2. `owners_after` can (almost) get arbitrary deeply nested,
        #          creating various complex threshold conditions:
        #          e.g. `transfer([inp1, inp2], [[a, [b, c]], d])`, means
        #               `a`'s signature would have a 50% weight on `inp1`
        #               compared to `b` and `c` that share 25% of the leftover
        #               weight respectively. `inp2` is owned completely by `d`.
        if len(inputs) == len(owners_after):
            if len(owners_after) == 1:
                conditions = [Condition.generate(owners_after)]
            elif len(owners_after) > 1:
                conditions = [Condition.generate(owners) for owners
                              in owners_after]
        else:
            raise ValueError("`inputs` and `owners_after`'s count must be the "
                             "same")

        data = Data(payload)
        inputs = deepcopy(inputs)
        return cls(cls.TRANSFER, inputs, conditions, data)

    def __eq__(self, other):
        try:
            other = other.to_dict()
        except AttributeError:
            return False
        return self.to_dict() == other

    def to_inputs(self, condition_indices=None):
        inputs = []
        # NOTE: If no condition indices are passed, we just assume to
        #       take all conditions as inputs.
        if condition_indices is None or len(condition_indices) == 0:
            condition_indices = [index for index, _
                                 in enumerate(self.conditions)]

        for cid in condition_indices:
            input_cond = self.conditions[cid]
            ffill = Fulfillment(input_cond.fulfillment,
                                input_cond.owners_after,
                                TransactionLink(self.id, cid))
            inputs.append(ffill)
        return inputs

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

    def sign(self, private_keys):
        # TODO: Singing should be possible with at least one of all private
        #       keys supplied to this method.
        """ Signs a transaction
            Acts as a proxy for `_sign_fulfillments`, for exposing a nicer API to the outside.
        """
        self._sign_fulfillments(private_keys)
        return self

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

        for index, (fulfillment, condition) in enumerate(zip(self.fulfillments, self.conditions)):
            # NOTE: We clone the current transaction but only add the condition and fulfillment we're currently
            # working on plus all previously signed ones.
            tx_partial = Transaction(self.operation, [fulfillment], [condition], self.data, self.timestamp,
                                     self.version)
            tx_serialized = Transaction._to_str(Transaction._remove_signatures(tx_partial.to_dict()))
            self._sign_fulfillment(fulfillment, index, tx_serialized, key_pairs)

    def _sign_fulfillment(self, fulfillment, index, tx_serialized, key_pairs):
        if isinstance(fulfillment.fulfillment, Ed25519Fulfillment):
            self._sign_simple_signature_fulfillment(fulfillment, index, tx_serialized, key_pairs)
        elif isinstance(fulfillment.fulfillment, ThresholdSha256Fulfillment):
            self._sign_threshold_signature_fulfillment(fulfillment, index, tx_serialized, key_pairs)
        else:
            raise ValueError("Fulfillment couldn't be matched to "
                             'Cryptocondition fulfillment type.')

    def _sign_simple_signature_fulfillment(self, fulfillment, index, tx_serialized, key_pairs):
        # NOTE: To eliminate the dangers of accidentially signing a condition by reference,
        #       we remove the reference of fulfillment here intentionally.
        #       If the user of this class knows how to use it, this should never happen,
        #       but then again, never say never.
        fulfillment = deepcopy(fulfillment)
        owner_before = fulfillment.owners_before[0]
        try:
            fulfillment.fulfillment.sign(tx_serialized, key_pairs[owner_before])
        except KeyError:
            raise KeypairMismatchException('Public key {} is not a pair to any of the private keys'
                                           .format(owner_before))
        self.fulfillments[index] = fulfillment

    def _sign_threshold_signature_fulfillment(self, fulfillment, index, tx_serialized, key_pairs):
        fulfillment = deepcopy(fulfillment)
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
        self.fulfillments[index] = fulfillment

    def fulfillments_valid(self, input_conditions=None):
        if self.operation in (Transaction.CREATE, Transaction.GENESIS):
            # NOTE: Since in the case of a create-transaction we do not have
            #       to check for input_conditions, we're just submitting dummy
            #       values to the actual method. This simplifies it's logic
            #       greatly, as we do not have to check against `None` values.
            return self._fulfillments_valid(['dummyvalue'
                                             for cond in self.fulfillments])
        elif self.operation == Transaction.TRANSFER:
            return self._fulfillments_valid([cond.fulfillment.condition_uri
                                             for cond in input_conditions])
        else:
            raise TypeError('`operation` must be either `TRANSFER`, `CREATE` or `GENESIS`')

    def _fulfillments_valid(self, input_condition_uris):
        input_condition_uris_count = len(input_condition_uris)
        fulfillments_count = len(self.fulfillments)
        conditions_count = len(self.conditions)

        def gen_tx(fulfillment, condition, input_condition_uri=None):
            tx = Transaction(self.operation, [fulfillment], [condition],
                             self.data, self.timestamp, self.version)
            tx_serialized = Transaction._to_str(Transaction._remove_signatures(tx.to_dict()))
            return Transaction._fulfillment_valid(fulfillment, self.operation,
                                                  tx_serialized,
                                                  input_condition_uri)

        if not fulfillments_count == conditions_count == input_condition_uris_count:
            raise ValueError('Fulfillments, conditions and input_condition_uris must have the same count')
        else:
            return reduce(and_, map(gen_tx, self.fulfillments, self.conditions, input_condition_uris))

    @staticmethod
    def _fulfillment_valid(fulfillment, operation, tx_serialized, input_condition_uri=None):
        try:
            parsed_fulfillment = CCFulfillment.from_uri(fulfillment.fulfillment.serialize_uri())
        except (TypeError, ValueError, ParsingError):
            return False
        if operation in (Transaction.CREATE, Transaction.GENESIS):
            input_condition_valid = True
        else:
            input_condition_valid = input_condition_uri == fulfillment.fulfillment.condition_uri

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
            'fulfillments': [fulfillment.to_dict(fid) for fid, fulfillment
                             in enumerate(self.fulfillments)],
            'conditions': [condition.to_dict(cid) for cid, condition
                           in enumerate(self.conditions)],
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
        # NOTE: We remove the reference since we need `tx_dict` only for the
        #       transaction's hash
        tx_dict = deepcopy(tx_dict)
        for fulfillment in tx_dict['transaction']['fulfillments']:
            # NOTE: Not all Cryptoconditions return a `signature` key (e.g.
            # ThresholdSha256Fulfillment), so setting it to `None` in any case
            # could yield incorrect signatures. This is why we only set it to
            # `None` if it's set in the dict.
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

    def __str__(self):
        tx = Transaction._remove_signatures(self.to_dict())
        return Transaction._to_str(tx)

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
