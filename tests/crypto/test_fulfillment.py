import binascii

from math import ceil

import pytest

from bigchaindb.crypto.condition import Condition
from bigchaindb.crypto.ed25519 import Ed25519SigningKey, Ed25519VerifyingKey
from bigchaindb.crypto.fulfillment import Fulfillment
from bigchaindb.crypto.fulfillments.ed25519_sha256 import Ed25519Sha256Fulfillment
from bigchaindb.crypto.fulfillments.sha256 import Sha256Fulfillment
from bigchaindb.crypto.fulfillments.threshold_sha256 import ThresholdSha256Fulfillment


class TestBigchainILPSha256Condition:

    def test_deserialize_condition(self, fulfillment_sha256):
        example_condition = fulfillment_sha256['condition_uri']
        condition = Condition.from_uri(example_condition)
        assert condition.serialize_uri() == fulfillment_sha256['condition_uri']

    def test_create_condition(self, fulfillment_sha256):
        sha256condition = Condition()
        sha256condition.bitmask = Sha256Fulfillment._bitmask
        sha256condition.hash = binascii.unhexlify(fulfillment_sha256['condition_hash'])
        sha256condition.max_fulfillment_length = 1
        assert sha256condition.serialize_uri() == fulfillment_sha256['condition_uri']


class TestBigchainILPSha256Fulfillment:

    def test_deserialize_and_validate_fulfillment(self, fulfillment_sha256):
        fulfillment = Fulfillment.from_uri(fulfillment_sha256['fulfillment_uri'])
        assert fulfillment.serialize_uri() == fulfillment_sha256['fulfillment_uri']
        assert fulfillment.condition.serialize_uri() == fulfillment_sha256['condition_uri']
        assert fulfillment.validate()

    def test_deserialize_condition_and_validate_fulfillment(self, fulfillment_sha256):
        condition = Condition.from_uri(fulfillment_sha256['condition_uri'])
        fulfillment = Sha256Fulfillment()
        fulfillment.preimage = ''
        assert fulfillment.serialize_uri() == fulfillment_sha256['fulfillment_uri']
        assert fulfillment.condition.serialize_uri() == condition.serialize_uri()
        assert fulfillment.validate()
        assert fulfillment.validate() \
            and fulfillment.condition.serialize_uri() == condition.serialize_uri()

    def test_condition_from_fulfillment(self):
        fulfillment = Sha256Fulfillment()
        with pytest.raises(ValueError):
            fulfillment.condition

        fulfillment.preimage = 'Hello World!'
        condition = fulfillment.condition

        verify_fulfillment = Sha256Fulfillment()
        verify_fulfillment.preimage = 'Hello World!'
        assert verify_fulfillment.condition.serialize_uri() == condition.serialize_uri()
        assert verify_fulfillment.validate()


class TestBigchainILPEd25519Sha256Fulfillment:

    def test_ilp_keys(self, sk_ilp, vk_ilp):
        sk = Ed25519SigningKey(sk_ilp['b58'])
        assert sk.to_ascii(encoding='base64') == sk_ilp['b64']
        assert binascii.hexlify(sk.to_bytes()[:32]) == sk_ilp['hex']

        vk = Ed25519VerifyingKey(vk_ilp['b58'])
        assert vk.to_ascii(encoding='base64') == vk_ilp['b64']
        assert binascii.hexlify(vk.to_bytes()) == vk_ilp['hex']

    def test_serialize_condition_and_validate_fulfillment(self, sk_ilp, vk_ilp, fulfillment_ed25519):
        sk = Ed25519SigningKey(sk_ilp['b58'])
        vk = Ed25519VerifyingKey(vk_ilp['b58'])

        fulfillment = Ed25519Sha256Fulfillment()
        fulfillment.public_key = vk
        fulfillment.message_prefix = 'Hello world!'
        fulfillment.max_dynamic_message_length = 32  # defaults to 0

        assert fulfillment.condition.serialize_uri() == fulfillment_ed25519['condition_uri']
        assert binascii.hexlify(fulfillment.condition.hash) == fulfillment_ed25519['condition_hash']

        fulfillment.message = ' Conditions are here!'

        # ED25519-SHA256 condition not fulfilled
        assert fulfillment.validate() == False

        # Fulfill an ED25519-SHA256 condition
        fulfillment.sign(sk)

        assert fulfillment.serialize_uri() == fulfillment_ed25519['fulfillment_uri']
        assert fulfillment.validate()

    def test_deserialize_condition(self, fulfillment_ed25519):
        deserialized_condition = Condition.from_uri(fulfillment_ed25519['condition_uri'])

        assert deserialized_condition.serialize_uri() == fulfillment_ed25519['condition_uri']
        assert binascii.hexlify(deserialized_condition.hash) == fulfillment_ed25519['condition_hash']

    def test_serialize_deserialize_condition(self, vk_ilp):
        vk = Ed25519VerifyingKey(vk_ilp['b58'])

        fulfillment = Ed25519Sha256Fulfillment()
        fulfillment.public_key = vk
        fulfillment.message_prefix = 'Hello world!'
        fulfillment.max_dynamic_message_length = 32

        condition = fulfillment.condition
        deserialized_condition = Condition.from_uri(condition.serialize_uri())

        assert deserialized_condition.bitmask == condition.bitmask
        assert deserialized_condition.hash == condition.hash
        assert deserialized_condition.max_fulfillment_length == condition.max_fulfillment_length
        assert deserialized_condition.serialize_uri() == condition.serialize_uri()

    def test_deserialize_fulfillment(self, vk_ilp, fulfillment_ed25519):
        fulfillment = Fulfillment.from_uri(fulfillment_ed25519['fulfillment_uri'])

        assert isinstance(fulfillment, Ed25519Sha256Fulfillment)
        assert fulfillment.serialize_uri() == fulfillment_ed25519['fulfillment_uri']
        assert fulfillment.condition.serialize_uri() == fulfillment_ed25519['condition_uri']
        assert binascii.hexlify(fulfillment.condition.hash) == fulfillment_ed25519['condition_hash']
        assert fulfillment.public_key.to_ascii(encoding='hex') == vk_ilp['hex']
        assert fulfillment.validate()

    def test_serialize_deserialize_fulfillment(self, sk_ilp, vk_ilp):
        sk = Ed25519SigningKey(sk_ilp['b58'])
        vk = Ed25519VerifyingKey(vk_ilp['b58'])

        fulfillment = Ed25519Sha256Fulfillment()
        fulfillment.public_key = vk
        fulfillment.message_prefix = 'Hello world!'
        fulfillment.max_dynamic_message_length = 32  # defaults to 0
        fulfillment.message = ' Conditions are here!'
        fulfillment.sign(sk)

        assert fulfillment.validate()

        deserialized_fulfillment = Fulfillment.from_uri(fulfillment.serialize_uri())
        assert isinstance(deserialized_fulfillment, Ed25519Sha256Fulfillment)
        assert deserialized_fulfillment.serialize_uri() == fulfillment.serialize_uri()
        assert deserialized_fulfillment.condition.serialize_uri() == fulfillment.condition.serialize_uri()
        assert deserialized_fulfillment.public_key.to_bytes() == fulfillment.public_key.to_bytes()
        assert deserialized_fulfillment.validate()


class TestBigchainILPThresholdSha256Fulfillment:

    def create_fulfillment_ed25519sha256(self, sk_ilp, vk_ilp):
        sk = Ed25519SigningKey(sk_ilp['b58'])
        vk = Ed25519VerifyingKey(vk_ilp['b58'])

        fulfillment = Ed25519Sha256Fulfillment()
        fulfillment.public_key = vk
        fulfillment.message_prefix = 'Hello world!'
        fulfillment.max_dynamic_message_length = 32  # defaults to 0
        fulfillment.message = ' Conditions are here!'
        fulfillment.sign(sk)
        return fulfillment

    def test_serialize_condition_and_validate_fulfillment(self,
                                                          fulfillment_sha256,
                                                          fulfillment_ed25519,
                                                          fulfillment_ed25519_2,
                                                          fulfillment_threshold):
        ilp_fulfillment = Fulfillment.from_uri(fulfillment_ed25519_2['fulfillment_uri'])
        ilp_fulfillment_2 = Fulfillment.from_uri(fulfillment_ed25519['fulfillment_uri'])
        ilp_fulfillment_3 = Fulfillment.from_uri(fulfillment_sha256['fulfillment_uri'])

        assert ilp_fulfillment.validate() == True
        assert ilp_fulfillment_2.validate() == True

        threshold = 2

        # Create a threshold condition
        fulfillment = ThresholdSha256Fulfillment()
        fulfillment.add_subfulfillment(ilp_fulfillment)
        fulfillment.add_subfulfillment(ilp_fulfillment_2)
        fulfillment.add_subfulfillment(ilp_fulfillment_3)
        fulfillment.threshold = threshold  # defaults to subconditions.length

        assert fulfillment.condition.serialize_uri() == fulfillment_threshold['condition_uri']
        # Note: If there are more than enough fulfilled subconditions, shorter
        # fulfillments will be chosen over longer ones.
        # thresholdFulfillmentUri.length === 65
        assert fulfillment.serialize_uri() == fulfillment_threshold['fulfillment_uri']
        assert fulfillment.validate()

    def test_deserialize_fulfillment(self,
                                     fulfillment_sha256,
                                     fulfillment_ed25519,
                                     fulfillment_threshold):
        num_fulfillments = 3
        threshold = 2

        fulfillment = Fulfillment.from_uri(fulfillment_threshold['fulfillment_uri'])
        assert isinstance(fulfillment, ThresholdSha256Fulfillment)
        assert fulfillment.threshold == threshold
        assert len(fulfillment.subfulfillments) == threshold
        assert len(fulfillment.get_all_subconditions()) == num_fulfillments
        assert fulfillment.serialize_uri() == fulfillment_threshold['fulfillment_uri']
        assert fulfillment.validate()
        assert isinstance(fulfillment.subfulfillments[0], Sha256Fulfillment)
        assert isinstance(fulfillment.subfulfillments[1], Ed25519Sha256Fulfillment)
        assert fulfillment.subfulfillments[0].condition.serialize_uri() == fulfillment_sha256['condition_uri']
        assert fulfillment.subfulfillments[1].condition.serialize_uri() == fulfillment_ed25519['condition_uri']

    def test_serialize_deserialize_fulfillment(self,
                                               fulfillment_ed25519):
        ilp_fulfillment = Fulfillment.from_uri(fulfillment_ed25519['fulfillment_uri'])
        num_fulfillments = 100
        threshold = ceil(num_fulfillments * 2 / 3)

        # Create a threshold condition
        fulfillment = ThresholdSha256Fulfillment()
        for i in range(num_fulfillments):
            fulfillment.add_subfulfillment(ilp_fulfillment)
        fulfillment.threshold = threshold

        fulfillment_uri = fulfillment.serialize_uri()

        assert fulfillment.validate()
        deserialized_fulfillment = Fulfillment.from_uri(fulfillment_uri)

        assert isinstance(deserialized_fulfillment, ThresholdSha256Fulfillment)
        assert deserialized_fulfillment.threshold == threshold
        assert len(deserialized_fulfillment.subfulfillments) == threshold
        assert len(deserialized_fulfillment.get_all_subconditions()) == num_fulfillments
        assert deserialized_fulfillment.serialize_uri() == fulfillment_uri
        assert deserialized_fulfillment.validate()

    def test_fulfillment_didnt_reach_threshold(self, fulfillment_ed25519):
        ilp_fulfillment = Fulfillment.from_uri(fulfillment_ed25519['fulfillment_uri'])
        threshold = 10

        # Create a threshold condition
        fulfillment = ThresholdSha256Fulfillment()
        fulfillment.threshold = threshold

        for i in range(threshold - 1):
            fulfillment.add_subfulfillment(ilp_fulfillment)

        with pytest.raises(ValueError):
            fulfillment.serialize_uri()

        assert fulfillment.validate() is False

        fulfillment.add_subfulfillment(ilp_fulfillment)

        fulfillment_uri = fulfillment.serialize_uri()
        assert fulfillment.validate()

        deserialized_fulfillment = Fulfillment.from_uri(fulfillment_uri)

        assert isinstance(deserialized_fulfillment, ThresholdSha256Fulfillment)
        assert deserialized_fulfillment.threshold == threshold
        assert len(deserialized_fulfillment.subfulfillments) == threshold
        assert len(deserialized_fulfillment.get_all_subconditions()) == threshold
        assert deserialized_fulfillment.serialize_uri() == fulfillment_uri
        assert deserialized_fulfillment.validate()

    def test_fulfillment_nested_and_or(self,
                                       fulfillment_sha256,
                                       fulfillment_ed25519,
                                       fulfillment_ed25519_2):
        ilp_fulfillment_sha = Fulfillment.from_uri(fulfillment_sha256['fulfillment_uri'])
        ilp_fulfillment_ed1 = Fulfillment.from_uri(fulfillment_ed25519_2['fulfillment_uri'])
        ilp_fulfillment_ed2 = Fulfillment.from_uri(fulfillment_ed25519['fulfillment_uri'])

        # 2-of-2 (AND with 2 inputs)
        fulfillment = ThresholdSha256Fulfillment()
        fulfillment.threshold = 2
        fulfillment.add_subfulfillment(ilp_fulfillment_sha)

        assert fulfillment.validate() is False

        # 1-of-2 (OR with 2 inputs)
        nested_fulfillment = ThresholdSha256Fulfillment()
        nested_fulfillment.threshold = 1
        nested_fulfillment.add_subfulfillment(ilp_fulfillment_ed1)
        assert nested_fulfillment.validate() is True
        nested_fulfillment.add_subfulfillment(ilp_fulfillment_ed2)
        assert nested_fulfillment.validate() is True

        fulfillment.add_subfulfillment(nested_fulfillment)
        assert fulfillment.validate() is True

        fulfillment_uri = fulfillment.serialize_uri()
        deserialized_fulfillment = Fulfillment.from_uri(fulfillment_uri)

        condition_uri = fulfillment.condition.serialize_uri()
        deserialized_condition = Condition.from_uri(condition_uri)

        assert isinstance(deserialized_fulfillment, ThresholdSha256Fulfillment)
        assert deserialized_fulfillment.threshold == 2
        assert len(deserialized_fulfillment.subfulfillments) == 2
        assert len(deserialized_fulfillment.subfulfillments[1].subfulfillments) == 1
        assert len(deserialized_fulfillment.get_all_subconditions()) == 2
        assert deserialized_fulfillment.serialize_uri() == fulfillment_uri
        assert deserialized_fulfillment.validate()
        assert deserialized_condition.serialize_uri() == condition_uri

    def test_fulfillment_nested(self,
                                fulfillment_sha256,
                                fulfillment_ed25519_2,):
        ilp_fulfillment_sha = Fulfillment.from_uri(fulfillment_sha256['fulfillment_uri'])
        ilp_fulfillment_ed1 = Fulfillment.from_uri(fulfillment_ed25519_2['fulfillment_uri'])

        # 2-of-2 (AND with 2 inputs)
        fulfillment = ThresholdSha256Fulfillment()
        fulfillment.threshold = 2
        fulfillment.add_subfulfillment(ilp_fulfillment_sha)

        max_depth = 10

        def add_nested_fulfillment(parent, current_depth=0):
            current_depth += 1
            child = ThresholdSha256Fulfillment()
            child.threshold = 1
            if current_depth < max_depth:
                add_nested_fulfillment(child, current_depth)
            else:
                child.add_subfulfillment(ilp_fulfillment_ed1)
            parent.add_subfulfillment(child)
            return parent

        fulfillment = add_nested_fulfillment(fulfillment)

        assert fulfillment.validate() is True
        assert len(fulfillment.subfulfillments) == 2
        assert isinstance(fulfillment.subfulfillments[1], ThresholdSha256Fulfillment)
        assert isinstance(fulfillment.subfulfillments[1].subfulfillments[0], ThresholdSha256Fulfillment)

        fulfillment_uri = fulfillment.serialize_uri()
        deserialized_fulfillment = Fulfillment.from_uri(fulfillment_uri)

        condition_uri = fulfillment.condition.serialize_uri()
        deserialized_condition = Condition.from_uri(condition_uri)

        assert deserialized_fulfillment.serialize_uri() == fulfillment_uri
        assert deserialized_fulfillment.validate() is True
        assert deserialized_condition.serialize_uri() == condition_uri
