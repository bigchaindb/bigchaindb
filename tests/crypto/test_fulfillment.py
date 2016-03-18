import binascii

from bigchaindb.crypto.condition import Condition
from bigchaindb.crypto.ed25519 import ED25519PrivateKey, ED25519PublicKey
from bigchaindb.crypto.fulfillment import Fulfillment
from bigchaindb.crypto.fulfillments.ed25519_sha256 import Ed25519Sha256Fulfillment


class TestBigchainILPFulfillmentEd25519Sha256:
    PUBLIC_HEX_ILP = b'ec172b93ad5e563bf4932c70e1245034c35467ef2efd4d64ebf819683467e2bf'
    PUBLIC_B64_ILP = b'7Bcrk61eVjv0kyxw4SRQNMNUZ+8u/U1k6/gZaDRn4r8'
    PUBLIC_B58_ILP = 'Gtbi6WQDB6wUePiZm8aYs5XZ5pUqx9jMMLvRVHPESTjU'

    PRIVATE_HEX_ILP = b'833fe62409237b9d62ec77587520911e9a759cec1d19755b7da901b96dca3d42'
    PRIVATE_B64_ILP = b'gz/mJAkje51i7HdYdSCRHpp1nOwdGXVbfakBuW3KPUI'
    PRIVATE_B58_ILP = '9qLvREC54mhKYivr88VpckyVWdAFmifJpGjbvV5AiTRs'

    CONDITION_ED25519_ILP = 'cc:1:8:qQINW2um59C4DB9JSVXH1igqAmaYGGqryllHUgCpfPU:113'
    FULFILLMENT_ED25519_ILP = \
        'cf:1:8:IOwXK5OtXlY79JMscOEkUDTDVGfvLv1NZOv4GWg0Z-K_DEhlbGxvIHdvcmxkISAVIENvbmRpdGlvbnMgYXJlIGhlcmUhQENbql531' \
        'PbCJlRUvKjP56k0XKJMOrIGo2F66ueuTtRnYrJB2t2ZttdfXM4gzD_87eH1nZTpu4rTkAx81hSdpwI'
    HASH_ED25519_HEX_ILP = b'a9020d5b6ba6e7d0b80c1f494955c7d6282a026698186aabca59475200a97cf5'

    def test_ilp_keys(self):
        sk = ED25519PrivateKey(self.PRIVATE_B58_ILP)
        assert sk.private_key.to_ascii(encoding='base64') == self.PRIVATE_B64_ILP
        assert binascii.hexlify(sk.private_key.to_bytes()[:32]) == self.PRIVATE_HEX_ILP

        vk = ED25519PublicKey(self.PUBLIC_B58_ILP)
        assert vk.public_key.to_ascii(encoding='base64') == self.PUBLIC_B64_ILP
        assert binascii.hexlify(vk.public_key.to_bytes()) == self.PUBLIC_HEX_ILP

    def test_serialize_condition_and_validate_fulfillment(self):
        sk = ED25519PrivateKey(self.PRIVATE_B58_ILP)
        vk = ED25519PublicKey(self.PUBLIC_B58_ILP)

        fulfillment = Ed25519Sha256Fulfillment()
        fulfillment.public_key = vk
        fulfillment.message_prefix = 'Hello world!'
        fulfillment.max_dynamic_message_length = 32  # defaults to 0

        assert fulfillment.condition.serialize_uri() == self.CONDITION_ED25519_ILP
        assert binascii.hexlify(fulfillment.condition.hash) == self.HASH_ED25519_HEX_ILP

        fulfillment.message = ' Conditions are here!'

        # ED25519-SHA256 condition not fulfilled
        assert fulfillment.validate() == False

        # Fulfill an ED25519-SHA256 condition
        fulfillment.sign(sk)

        assert fulfillment.serialize_uri() == self.FULFILLMENT_ED25519_ILP
        assert fulfillment.validate()

    def test_deserialize_condition(self):

        deserialized_condition = Condition.from_uri(self.CONDITION_ED25519_ILP)

        assert deserialized_condition.serialize_uri() == self.CONDITION_ED25519_ILP
        assert binascii.hexlify(deserialized_condition.hash) == self.HASH_ED25519_HEX_ILP

    def test_serialize_deserialize_condition(self):
        vk = ED25519PublicKey(self.PUBLIC_B58_ILP)

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

    def test_deserialize_fulfillment(self):
        fulfillment = Fulfillment.from_uri(self.FULFILLMENT_ED25519_ILP)

        assert fulfillment.serialize_uri() == self.FULFILLMENT_ED25519_ILP
        assert fulfillment.condition.serialize_uri() == self.CONDITION_ED25519_ILP
        assert binascii.hexlify(fulfillment.condition.hash) == self.HASH_ED25519_HEX_ILP
        assert fulfillment.public_key.public_key.to_ascii(encoding='hex') == self.PUBLIC_HEX_ILP
        assert fulfillment.validate()

    def test_serializer_deserialize_fulfillment(self):
        sk = ED25519PrivateKey(self.PRIVATE_B58_ILP)
        vk = ED25519PublicKey(self.PUBLIC_B58_ILP)

        fulfillment = Ed25519Sha256Fulfillment()
        fulfillment.public_key = vk
        fulfillment.message_prefix = 'Hello world!'
        fulfillment.max_dynamic_message_length = 32  # defaults to 0
        fulfillment.message = ' Conditions are here!'
        fulfillment.sign(sk)

        assert fulfillment.validate()

        deserialized_fulfillment = Fulfillment.from_uri(fulfillment.serialize_uri())
        assert deserialized_fulfillment.serialize_uri() == fulfillment.serialize_uri()
        assert deserialized_fulfillment.condition.serialize_uri() == fulfillment.condition.serialize_uri()
        assert deserialized_fulfillment.public_key.public_key.to_bytes() == fulfillment.public_key.public_key.to_bytes()
        assert deserialized_fulfillment.validate()


class TestBigchainILPConditionSha256:

    CONDITION_SHA256_ILP = 'cc:1:1:47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU:1'

    def test_deserialize_condition(self):
        example_condition = self.CONDITION_SHA256_ILP
        condition = Condition.from_uri(example_condition)
        assert condition.serialize_uri() == self.CONDITION_SHA256_ILP
