import json
from time import sleep

import cryptoconditions as cc

from bigchaindb import Bigchain, util, crypto, exceptions


b = Bigchain()

"""
Create a Digital Asset
"""

# create a test user
testuser1_priv, testuser1_pub = crypto.generate_key_pair()

# define a digital asset data payload
digital_asset_payload = {'msg': 'Hello BigchainDB!'}

# a create transaction uses the operation `CREATE` and has no inputs
tx = b.create_transaction(b.me, testuser1_pub, None, 'CREATE', payload=digital_asset_payload)

# all transactions need to be signed by the user creating the transaction
tx_signed = b.sign_transaction(tx, b.me_private)

# write the transaction to the bigchain
# the transaction will be stored in a backlog where it will be validated,
# included in a block, and written to the bigchain
b.write_transaction(tx_signed)

sleep(10)

"""
Read the Creation Transaction from the DB
"""

tx_retrieved = b.get_transaction(tx_signed['id'])

print(json.dumps(tx_retrieved, sort_keys=True, indent=4, separators=(',', ':')))

print(testuser1_pub)
print(b.me)

print(tx_retrieved['id'])

"""
Transfer the Digital Asset
"""

# create a second testuser
testuser2_priv, testuser2_pub = crypto.generate_key_pair()

# retrieve the transaction with condition id
tx_retrieved_id = b.get_owned_ids(testuser1_pub).pop()
print(json.dumps(tx_retrieved_id, sort_keys=True, indent=4, separators=(',', ':')))

# create a transfer transaction
tx_transfer = b.create_transaction(testuser1_pub, testuser2_pub, tx_retrieved_id, 'TRANSFER')

# sign the transaction
tx_transfer_signed = b.sign_transaction(tx_transfer, testuser1_priv)

# write the transaction
b.write_transaction(tx_transfer_signed)

sleep(10)

# check if the transaction is already in the bigchain
tx_transfer_retrieved = b.get_transaction(tx_transfer_signed['id'])
print(json.dumps(tx_transfer_retrieved, sort_keys=True, indent=4, separators=(',', ':')))

"""
Double Spends
"""

# create another transfer transaction with the same input
tx_transfer2 = b.create_transaction(testuser1_pub, testuser2_pub, tx_retrieved_id, 'TRANSFER')

# sign the transaction
tx_transfer_signed2 = b.sign_transaction(tx_transfer2, testuser1_priv)

# check if the transaction is valid
try:
    b.validate_transaction(tx_transfer_signed2)
except exceptions.DoubleSpend as e:
    print(e)

"""
Multiple Owners
"""

# Create a new asset and assign it to multiple owners
tx_multisig = b.create_transaction(b.me, [testuser1_pub, testuser2_pub], None, 'CREATE')

# Have the federation sign the transaction
tx_multisig_signed = b.sign_transaction(tx_multisig, b.me_private)
b.write_transaction(tx_multisig_signed)

# wait a few seconds for the asset to appear on the blockchain
sleep(10)

# retrieve the transaction
tx_multisig_retrieved = b.get_transaction(tx_multisig_signed['id'])

print(json.dumps(tx_multisig_retrieved, sort_keys=True, indent=4, separators=(',', ':')))

testuser3_priv, testuser3_pub = crypto.generate_key_pair()

tx_multisig_retrieved_id = b.get_owned_ids(testuser2_pub).pop()
tx_multisig_transfer = b.create_transaction([testuser1_pub, testuser2_pub], testuser3_pub, tx_multisig_retrieved_id, 'TRANSFER')
tx_multisig_transfer_signed = b.sign_transaction(tx_multisig_transfer, [testuser1_priv, testuser2_priv])

b.write_transaction(tx_multisig_transfer_signed)

# wait a few seconds for the asset to appear on the blockchain
sleep(10)

# retrieve the transaction
tx_multisig_retrieved = b.get_transaction(tx_multisig_transfer_signed['id'])

print(json.dumps(tx_multisig_transfer_signed, sort_keys=True, indent=4, separators=(',', ':')))

"""
Multiple Inputs and Outputs
"""
for i in range(3):
    tx_mimo_asset = b.create_transaction(b.me, testuser1_pub, None, 'CREATE')
    tx_mimo_asset_signed = b.sign_transaction(tx_mimo_asset, b.me_private)
    b.write_transaction(tx_mimo_asset_signed)

sleep(10)

# get inputs
owned_mimo_inputs = b.get_owned_ids(testuser1_pub)
print(len(owned_mimo_inputs))

# create a transaction
tx_mimo = b.create_transaction(testuser1_pub, testuser2_pub, owned_mimo_inputs, 'TRANSFER')
tx_mimo_signed = b.sign_transaction(tx_mimo, testuser1_priv)

# write the transaction
b.write_transaction(tx_mimo_signed)

print(json.dumps(tx_mimo_signed, sort_keys=True, indent=4, separators=(',', ':')))

"""
Threshold Conditions
"""

# create some new testusers
thresholduser1_priv, thresholduser1_pub = crypto.generate_key_pair()
thresholduser2_priv, thresholduser2_pub = crypto.generate_key_pair()
thresholduser3_priv, thresholduser3_pub = crypto.generate_key_pair()

# retrieve the last transaction of testuser2
tx_retrieved_id = b.get_owned_ids(testuser2_pub).pop()

# create a base template for a 1-input/3-output transaction
threshold_tx = b.create_transaction(testuser2_pub, [thresholduser1_pub, thresholduser2_pub, thresholduser3_pub],
                                    tx_retrieved_id, 'TRANSFER')

# create a 2-out-of-3 Threshold Cryptocondition
threshold_condition = cc.ThresholdSha256Fulfillment(threshold=2)
threshold_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=thresholduser1_pub))
threshold_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=thresholduser2_pub))
threshold_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=thresholduser3_pub))

# update the condition in the newly created transaction
threshold_tx['transaction']['conditions'][0]['condition'] = {
    'details': json.loads(threshold_condition.serialize_json()),
    'uri': threshold_condition.condition.serialize_uri()
}

# conditions have been updated, so hash needs updating
threshold_tx['id'] = util.get_hash_data(threshold_tx)

# sign the transaction
threshold_tx_signed = b.sign_transaction(threshold_tx, testuser2_priv)

# write the transaction
b.write_transaction(threshold_tx_signed)

sleep(10)

# check if the transaction is already in the bigchain
tx_threshold_retrieved = b.get_transaction(threshold_tx_signed['id'])
print(json.dumps(tx_threshold_retrieved, sort_keys=True, indent=4, separators=(',', ':')))

thresholduser4_priv, thresholduser4_pub = crypto.generate_key_pair()

# retrieve the last transaction of thresholduser1_pub
tx_retrieved_id = b.get_owned_ids(thresholduser1_pub).pop()

# create a base template for a 2-input/1-output transaction
threshold_tx_transfer = b.create_transaction([thresholduser1_pub, thresholduser2_pub, thresholduser3_pub],
                                             thresholduser4_pub, tx_retrieved_id, 'TRANSFER')

# parse the threshold cryptocondition
threshold_fulfillment = cc.Fulfillment.from_json(threshold_tx['transaction']['conditions'][0]['condition']['details'])

subfulfillment1 = threshold_fulfillment.get_subcondition_from_vk(thresholduser1_pub)[0]
subfulfillment2 = threshold_fulfillment.get_subcondition_from_vk(thresholduser2_pub)[0]
subfulfillment3 = threshold_fulfillment.get_subcondition_from_vk(thresholduser3_pub)[0]


# get the fulfillment message to sign
threshold_tx_fulfillment_message = util.get_fulfillment_message(threshold_tx_transfer,
                                                                threshold_tx_transfer['transaction']['fulfillments'][0],
                                                                serialized=True)

# clear the subconditions of the threshold fulfillment, they will be added again after signing
threshold_fulfillment.subconditions = []

# sign and add the subconditions until threshold of 2 is reached
subfulfillment1.sign(threshold_tx_fulfillment_message, crypto.SigningKey(thresholduser1_priv))
threshold_fulfillment.add_subfulfillment(subfulfillment1)
subfulfillment2.sign(threshold_tx_fulfillment_message, crypto.SigningKey(thresholduser2_priv))
threshold_fulfillment.add_subfulfillment(subfulfillment2)

# Add remaining (unfulfilled) fulfillment as a condition
threshold_fulfillment.add_subcondition(subfulfillment3.condition)

assert threshold_fulfillment.validate(threshold_tx_fulfillment_message) == True

threshold_tx_transfer['transaction']['fulfillments'][0]['fulfillment'] = threshold_fulfillment.serialize_uri()

assert b.verify_signature(threshold_tx_transfer) == True

assert b.validate_transaction(threshold_tx_transfer) == threshold_tx_transfer

b.write_transaction(threshold_tx_transfer)

print(json.dumps(threshold_tx_transfer, sort_keys=True, indent=4, separators=(',', ':')))


