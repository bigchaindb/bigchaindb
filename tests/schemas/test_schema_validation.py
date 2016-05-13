

def test_valid_transaction_should_pass(b, transaction_schema, user_sk, user_vk):
    from jsonschema import validate
    from bigchaindb import util

    tx = util.create_tx(user_vk, user_vk, None, 'CREATE')
    tx = util.transform_create(tx)
    tx = util.sign_tx(tx, b.me_private)

    validate(tx, transaction_schema)

