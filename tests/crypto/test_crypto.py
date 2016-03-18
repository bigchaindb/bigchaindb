import base64

from bigchaindb.crypto.ecdsa import EcdsaSigningKey, EcdsaVerifyingKey, ecdsa_generate_key_pair
from bigchaindb.crypto.ed25519 import Ed25519SigningKey, Ed25519VerifyingKey, ed25519_generate_key_pair


class TestBigchainCryptoED25519(object):
    PRIVATE_B64 = b'xSrGKGxeJYVlVrk84f29wcPazoTV+y8fzM7P0iFsSdg='
    PRIVATE_BYTES = b'\xc5*\xc6(l^%\x85eV\xb9<\xe1\xfd\xbd\xc1\xc3\xda\xce\x84\xd5\xfb/\x1f\xcc\xce\xcf\xd2!lI\xd8v\x08\xfb\x03\x15y/&\xcd^O\xa9\xb8\xd2\x8a\x89\x8d\xf94\x9b\xbe\xb1\xe7\xdb~\x95!o\xde\xa2{\xa5'
    PRIVATE_B58 = 'EGf9UJzryLpZaBguyf5f4QAefFnairNbHLkhht8BZ57m'

    PUBLIC_B64 = b'dgj7AxV5LybNXk+puNKKiY35NJu+sefbfpUhb96ie6U='
    PUBLIC_BYTES = b'v\x08\xfb\x03\x15y/&\xcd^O\xa9\xb8\xd2\x8a\x89\x8d\xf94\x9b\xbe\xb1\xe7\xdb~\x95!o\xde\xa2{\xa5'
    PUBLIC_B58 = '8wm3wiqsoujkDJvk8FMZkHijb9eZdUqMuZsnRee4eRz4'

    PUBLIC_B64_ILP = 'Lvf3YtnHLMER+VHT0aaeEJF+7WQcvp4iKZAdvMVto7c='
    MSG_SHA512_ILP = 'claZQU7qkFz7smkAVtQp9ekUCc5LgoeN9W3RItIzykNEDbGSvzeHvOk9v/vrPpm+XWx5VFjd/sVbM2SLnCpxLw=='
    SIG_B64_ILP = 'sd0RahwuJJgeNfg8HvWHtYf4uqNgCOqIbseERacqs8G0kXNQQnhfV6gWAnMb+0RIlY3e0mqbrQiUwbRYJvRBAw=='

    def test_private_key_encode(self):
        private_value_base58 = Ed25519SigningKey.encode(self.PRIVATE_B64)
        assert private_value_base58 == self.PRIVATE_B58

    def test_private_key_init(self):
        sk = Ed25519SigningKey(self.PRIVATE_B58)
        assert sk.to_ascii(encoding='base64') == self.PRIVATE_B64[:-1]
        assert sk.to_bytes() == self.PRIVATE_BYTES

    def test_private_key_decode(self):
        private_value = Ed25519SigningKey.decode(self.PRIVATE_B58)
        assert private_value == self.PRIVATE_B64

    def test_public_key_encode(self):
        public_value_base58 = Ed25519VerifyingKey.encode(self.PUBLIC_B64)
        assert public_value_base58 == self.PUBLIC_B58

    def test_public_key_init(self):
        vk = Ed25519VerifyingKey(self.PUBLIC_B58)
        assert vk.to_ascii(encoding='base64') == self.PUBLIC_B64[:-1]
        assert vk.to_bytes() == self.PUBLIC_BYTES

    def test_public_key_decode(self):
        public_value = Ed25519VerifyingKey.decode(self.PUBLIC_B58)
        assert public_value == self.PUBLIC_B64

    def test_sign_verify(self):
        message = 'Hello World!'
        sk = Ed25519SigningKey(self.PRIVATE_B58)
        vk = Ed25519VerifyingKey(self.PUBLIC_B58)
        assert vk.verify(message, sk.sign(message)) is True
        assert vk.verify(message, sk.sign(message + 'dummy')) is False
        assert vk.verify(message + 'dummy', sk.sign(message)) is False
        vk = Ed25519VerifyingKey(Ed25519VerifyingKey.encode(self.PUBLIC_B64_ILP))
        assert vk.verify(message, sk.sign(message)) is False

    def test_valid_condition_valid_signature_ilp(self):
        vk = Ed25519VerifyingKey(Ed25519VerifyingKey.encode(self.PUBLIC_B64_ILP))
        msg = self.MSG_SHA512_ILP
        sig = self.SIG_B64_ILP
        assert vk.verify(base64.b64decode(msg), base64.b64decode(sig), encoding=None) is True

    def test_valid_condition_invalid_signature_ilp(self):
        vk = Ed25519VerifyingKey(Ed25519VerifyingKey.encode(self.PUBLIC_B64_ILP))
        msg = self.MSG_SHA512_ILP
        sig = self.MSG_SHA512_ILP
        assert vk.verify(base64.b64decode(msg), base64.b64decode(sig), encoding=None) is False

    def test_generate_key_pair(self):
        sk, vk = ed25519_generate_key_pair()
        assert Ed25519SigningKey.encode(Ed25519SigningKey.decode(sk)) == sk
        assert Ed25519VerifyingKey.encode(Ed25519VerifyingKey.decode(vk)) == vk

    def test_generate_sign_verify(self):
        sk, vk = ed25519_generate_key_pair()
        sk = Ed25519SigningKey(sk)
        vk = Ed25519VerifyingKey(vk)
        message = 'Hello World!'
        assert vk.verify(message, sk.sign(message)) is True
        assert vk.verify(message, sk.sign(message + 'dummy')) is False
        assert vk.verify(message + 'dummy', sk.sign(message)) is False
        vk = Ed25519VerifyingKey(Ed25519VerifyingKey.encode(self.PUBLIC_B64_ILP))
        assert vk.verify(message, sk.sign(message)) is False


class TestBigchainCryptoECDSA(object):
    PRIVATE_VALUE = 64328150571824492670917070117568709277186368319388887463636481841106388379832
    PUBLIC_VALUE_X = 48388170575736684074633245566225141536152842355597159440179742847497614196929
    PUBLIC_VALUE_Y = 65233479152484407841598798165960909560839872511163322973341535484598825150846

    PRIVATE_VALUE_B58 = 'AaAp4xBavbe6VGeQF2mWdSKNM1r6HfR2Z1tAY6aUkwdq'
    PUBLIC_VALUE_COMPRESSED_B58 = 'ifEi3UuTDT4CqUUKiS5omgeDodhu2aRFHVp6LoahbEVe'

    def test_private_key_encode(self):
        private_value_base58 = EcdsaSigningKey.encode(self.PRIVATE_VALUE)
        assert private_value_base58 == self.PRIVATE_VALUE_B58

    def test_private_key_decode(self):
        private_value = EcdsaSigningKey.decode(self.PRIVATE_VALUE_B58)
        assert private_value == self.PRIVATE_VALUE

    def test_public_key_encode(self):
        public_value_compressed_base58 = EcdsaVerifyingKey.encode(self.PUBLIC_VALUE_X, self.PUBLIC_VALUE_Y)
        assert public_value_compressed_base58 == self.PUBLIC_VALUE_COMPRESSED_B58

    def test_public_key_decode(self):
        public_value_x, public_value_y = EcdsaVerifyingKey.decode(self.PUBLIC_VALUE_COMPRESSED_B58)
        assert public_value_x == self.PUBLIC_VALUE_X
        assert public_value_y == self.PUBLIC_VALUE_Y

    def test_sign_verify(self):
        message = 'Hello World!'
        public_key = EcdsaVerifyingKey(self.PUBLIC_VALUE_COMPRESSED_B58)
        private_key = EcdsaSigningKey(self.PRIVATE_VALUE_B58)
        assert public_key.verify(message, private_key.sign(message)) is True

    def test_generate_key_pair(self):
        private_value_base58, public_value_compressed_base58 = ecdsa_generate_key_pair()
        assert EcdsaSigningKey.encode(
            EcdsaSigningKey.decode(private_value_base58)) == private_value_base58
        assert EcdsaVerifyingKey.encode(
            *EcdsaVerifyingKey.decode(public_value_compressed_base58)) == public_value_compressed_base58
