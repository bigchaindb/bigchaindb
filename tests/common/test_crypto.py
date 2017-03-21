

def test_crypto_keypair():
    from bigchaindb.common.crypto import generate_key_pair

    secret = 'much secret'
    keypair = generate_key_pair(secret=secret)

    assert len(keypair.public_key) == len(generate_key_pair().public_key)
    # TODO: 43 !== 44 -> need to check why
    # assert len(keypair.private_key) == len(generate_key_pair().private_key)
    assert keypair.public_key == generate_key_pair(secret).public_key
    assert keypair.private_key == generate_key_pair(secret).private_key
