import json
from time import sleep

import cryptoconditions as cc
from bigchaindb.common.util import gen_timestamp

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

sleep(8)

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


b.validate_transaction(tx_transfer_signed)
# write the transaction
b.write_transaction(tx_transfer_signed)

sleep(8)

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

b.validate_transaction(tx_multisig_signed)
b.write_transaction(tx_multisig_signed)

# wait a few seconds for the asset to appear on the blockchain
sleep(8)

# retrieve the transaction
tx_multisig_retrieved = b.get_transaction(tx_multisig_signed['id'])
assert tx_multisig_retrieved is not None

print(json.dumps(tx_multisig_retrieved, sort_keys=True, indent=4, separators=(',', ':')))

testuser3_priv, testuser3_pub = crypto.generate_key_pair()

tx_multisig_retrieved_id = b.get_owned_ids(testuser2_pub).pop()
tx_multisig_transfer = b.create_transaction([testuser1_pub, testuser2_pub], testuser3_pub, tx_multisig_retrieved_id, 'TRANSFER')
tx_multisig_transfer_signed = b.sign_transaction(tx_multisig_transfer, [testuser1_priv, testuser2_priv])

try:
    b.validate_transaction(tx_multisig_transfer_signed)
except exceptions.InvalidSignature:
    # import ipdb; ipdb.set_trace()
    b.validate_transaction(tx_multisig_transfer_signed)
b.write_transaction(tx_multisig_transfer_signed)

# wait a few seconds for the asset to appear on the blockchain
sleep(8)

# retrieve the transaction
tx_multisig_transfer_retrieved = b.get_transaction(tx_multisig_transfer_signed['id'])
assert tx_multisig_transfer_retrieved is not None
print(json.dumps(tx_multisig_transfer_retrieved, sort_keys=True, indent=4, separators=(',', ':')))

"""
Multiple Inputs and Outputs
"""
for i in range(3):
    tx_mimo_asset = b.create_transaction(b.me, testuser1_pub, None, 'CREATE')
    tx_mimo_asset_signed = b.sign_transaction(tx_mimo_asset, b.me_private)
    b.validate_transaction(tx_mimo_asset_signed)
    b.write_transaction(tx_mimo_asset_signed)

sleep(8)

# get inputs
owned_mimo_inputs = b.get_owned_ids(testuser1_pub)
print(len(owned_mimo_inputs))

# create a transaction
tx_mimo = b.create_transaction(testuser1_pub, testuser2_pub, owned_mimo_inputs, 'TRANSFER')

tx_mimo_signed = b.sign_transaction(tx_mimo, testuser1_priv)
# write the transaction
b.validate_transaction(tx_mimo_signed)
b.write_transaction(tx_mimo_signed)

print(json.dumps(tx_mimo_signed, sort_keys=True, indent=4, separators=(',', ':')))

sleep(8)

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
    'details': threshold_condition.to_dict(),
    'uri': threshold_condition.condition.serialize_uri()
}

# conditions have been updated, so hash needs updating
threshold_tx['id'] = util.get_hash_data(threshold_tx)

# sign the transaction
threshold_tx_signed = b.sign_transaction(threshold_tx, testuser2_priv)

b.validate_transaction(threshold_tx_signed)
# write the transaction
b.write_transaction(threshold_tx_signed)

sleep(8)

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
threshold_fulfillment = cc.Fulfillment.from_dict(threshold_tx['transaction']['conditions'][0]['condition']['details'])

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

assert b.validate_fulfillments(threshold_tx_transfer) == True

assert b.validate_transaction(threshold_tx_transfer) == threshold_tx_transfer

b.write_transaction(threshold_tx_transfer)

print(json.dumps(threshold_tx_transfer, sort_keys=True, indent=4, separators=(',', ':')))

"""
Hashlocked Conditions
"""

# Create a hash-locked asset without any owners_after
hashlock_tx = b.create_transaction(b.me, None, None, 'CREATE')

# Define a secret that will be hashed - fulfillments need to guess the secret
secret = b'much secret! wow!'
first_tx_condition = cc.PreimageSha256Fulfillment(preimage=secret)

# The conditions list is empty, so we need to append a new condition
hashlock_tx['transaction']['conditions'].append({
    'condition': {
        'uri': first_tx_condition.condition.serialize_uri()
    },
    'cid': 0,
    'owners_after': None
})

# Conditions have been updated, so hash needs updating
hashlock_tx['id'] = util.get_hash_data(hashlock_tx)

# The asset needs to be signed by the owner_before
hashlock_tx_signed = b.sign_transaction(hashlock_tx, b.me_private)

# Some validations
assert b.validate_transaction(hashlock_tx_signed) == hashlock_tx_signed
assert b.is_valid_transaction(hashlock_tx_signed) == hashlock_tx_signed

b.write_transaction(hashlock_tx_signed)
print(json.dumps(hashlock_tx_signed, sort_keys=True, indent=4, separators=(',', ':')))

sleep(8)

hashlockuser_priv, hashlockuser_pub = crypto.generate_key_pair()

# create hashlock fulfillment tx
hashlock_fulfill_tx = b.create_transaction(None, hashlockuser_priv, {'txid': hashlock_tx['id'], 'cid': 0}, 'TRANSFER')

# try a wrong secret
hashlock_fulfill_tx_fulfillment = cc.PreimageSha256Fulfillment(preimage=b'')
hashlock_fulfill_tx['transaction']['fulfillments'][0]['fulfillment'] = \
    hashlock_fulfill_tx_fulfillment.serialize_uri()

assert b.is_valid_transaction(hashlock_fulfill_tx) == False

# provide the right secret
hashlock_fulfill_tx_fulfillment = cc.PreimageSha256Fulfillment(preimage=secret)
hashlock_fulfill_tx['transaction']['fulfillments'][0]['fulfillment'] = \
    hashlock_fulfill_tx_fulfillment.serialize_uri()

assert b.validate_transaction(hashlock_fulfill_tx) == hashlock_fulfill_tx
assert b.is_valid_transaction(hashlock_fulfill_tx) == hashlock_fulfill_tx

b.write_transaction(hashlock_fulfill_tx)
print(json.dumps(hashlock_fulfill_tx, sort_keys=True, indent=4, separators=(',', ':')))


"""
Timeout Conditions
"""
# Create transaction template
tx_timeout = b.create_transaction(b.me, None, None, 'CREATE')

# Set expiry time (12 secs from now)
time_sleep = 12
time_expire = str(float(gen_timestamp()) + time_sleep)

# only valid if the server time <= time_expire
condition_timeout = cc.TimeoutFulfillment(expire_time=time_expire)

# The conditions list is empty, so we need to append a new condition
tx_timeout['transaction']['conditions'].append({
    'condition': {
        'details': condition_timeout.to_dict(),
        'uri': condition_timeout.condition.serialize_uri()
    },
    'cid': 0,
    'owners_after': None
})

# conditions have been updated, so hash needs updating
tx_timeout['id'] = util.get_hash_data(tx_timeout)

# sign transaction
tx_timeout_signed = b.sign_transaction(tx_timeout, b.me_private)

b.write_transaction(tx_timeout_signed)
print(json.dumps(tx_timeout, sort_keys=True, indent=4, separators=(',', ':')))
sleep(8)

# Retrieve the transaction id of tx_timeout
tx_timeout_id = {'txid': tx_timeout['id'], 'cid': 0}

# Create a template to transfer the tx_timeout
tx_timeout_transfer = b.create_transaction(None, testuser1_pub, tx_timeout_id, 'TRANSFER')

# Parse the threshold cryptocondition
timeout_fulfillment = cc.Fulfillment.from_dict(
    tx_timeout['transaction']['conditions'][0]['condition']['details'])

tx_timeout_transfer['transaction']['fulfillments'][0]['fulfillment'] = timeout_fulfillment.serialize_uri()

# no need to sign transaction, like with hashlocks
for i in range(time_sleep - 4):
    tx_timeout_valid = b.is_valid_transaction(tx_timeout_transfer) == tx_timeout_transfer
    seconds_to_timeout = int(float(time_expire) - float(gen_timestamp()))
    print('tx_timeout valid: {} ({}s to timeout)'.format(tx_timeout_valid, seconds_to_timeout))
    sleep(1)

"""
Escrow Conditions
"""
# retrieve the last transaction of testuser2
tx_retrieved_id = b.get_owned_ids(testuser2_pub).pop()

# Create escrow template with the execute and abort address
tx_escrow = b.create_transaction(testuser2_pub, [testuser2_pub, testuser1_pub], tx_retrieved_id, 'TRANSFER')

# Set expiry time (12 secs from now)
time_sleep = 12
time_expire = str(float(gen_timestamp()) + time_sleep)

# Create escrow and timeout condition
condition_escrow = cc.ThresholdSha256Fulfillment(threshold=1)  # OR Gate
condition_timeout = cc.TimeoutFulfillment(expire_time=time_expire)  # only valid if now() <= time_expire
condition_timeout_inverted = cc.InvertedThresholdSha256Fulfillment(threshold=1)
condition_timeout_inverted.add_subfulfillment(condition_timeout)

# Create execute branch
condition_execute = cc.ThresholdSha256Fulfillment(threshold=2)  # AND gate
condition_execute.add_subfulfillment(cc.Ed25519Fulfillment(public_key=testuser1_pub))  # execute address
condition_execute.add_subfulfillment(condition_timeout)  # federation checks on expiry
condition_escrow.add_subfulfillment(condition_execute)

# Create abort branch
condition_abort = cc.ThresholdSha256Fulfillment(threshold=2)  # AND gate
condition_abort.add_subfulfillment(cc.Ed25519Fulfillment(public_key=testuser2_pub))  # abort address
condition_abort.add_subfulfillment(condition_timeout_inverted)
condition_escrow.add_subfulfillment(condition_abort)

# Update the condition in the newly created transaction
tx_escrow['transaction']['conditions'][0]['condition'] = {
    'details': condition_escrow.to_dict(),
    'uri': condition_escrow.condition.serialize_uri()
}

# conditions have been updated, so hash needs updating
tx_escrow['id'] = util.get_hash_data(tx_escrow)

# sign transaction
tx_escrow_signed = b.sign_transaction(tx_escrow, testuser2_priv)

# some checks
assert b.validate_transaction(tx_escrow_signed) == tx_escrow_signed
assert b.is_valid_transaction(tx_escrow_signed) == tx_escrow_signed

print(json.dumps(tx_escrow_signed, sort_keys=True, indent=4, separators=(',', ':')))
b.write_transaction(tx_escrow_signed)
sleep(8)

# Retrieve the last transaction of thresholduser1_pub
tx_escrow_id = {'txid': tx_escrow_signed['id'], 'cid': 0}

# Create a base template for output transaction
tx_escrow_execute = b.create_transaction([testuser2_pub, testuser1_pub], testuser1_pub, tx_escrow_id, 'TRANSFER')

# Parse the threshold cryptocondition
escrow_fulfillment = cc.Fulfillment.from_dict(
    tx_escrow['transaction']['conditions'][0]['condition']['details'])

subfulfillment_testuser1 = escrow_fulfillment.get_subcondition_from_vk(testuser1_pub)[0]
subfulfillment_testuser2 = escrow_fulfillment.get_subcondition_from_vk(testuser2_pub)[0]
subfulfillment_timeout = escrow_fulfillment.subconditions[0]['body'].subconditions[1]['body']
subfulfillment_timeout_inverted = escrow_fulfillment.subconditions[1]['body'].subconditions[1]['body']

# Get the fulfillment message to sign
tx_escrow_execute_fulfillment_message = \
    util.get_fulfillment_message(tx_escrow_execute,
                                 tx_escrow_execute['transaction']['fulfillments'][0],
                                 serialized=True)

escrow_fulfillment.subconditions = []

# fulfill execute branch
fulfillment_execute = cc.ThresholdSha256Fulfillment(threshold=2)
subfulfillment_testuser1.sign(tx_escrow_execute_fulfillment_message, crypto.SigningKey(testuser1_priv))
fulfillment_execute.add_subfulfillment(subfulfillment_testuser1)
fulfillment_execute.add_subfulfillment(subfulfillment_timeout)
escrow_fulfillment.add_subfulfillment(fulfillment_execute)

# do not fulfill abort branch
condition_abort = cc.ThresholdSha256Fulfillment(threshold=2)
condition_abort.add_subfulfillment(subfulfillment_testuser2)
condition_abort.add_subfulfillment(subfulfillment_timeout_inverted)
escrow_fulfillment.add_subcondition(condition_abort.condition)

# create fulfillment and append to transaction
tx_escrow_execute['transaction']['fulfillments'][0]['fulfillment'] = escrow_fulfillment.serialize_uri()

# Time has expired, hence the abort branch can redeem
tx_escrow_abort = b.create_transaction([testuser2_pub, testuser1_pub], testuser2_pub, tx_escrow_id, 'TRANSFER')

# Parse the threshold cryptocondition
escrow_fulfillment = cc.Fulfillment.from_dict(
    tx_escrow['transaction']['conditions'][0]['condition']['details'])

subfulfillment_testuser1 = escrow_fulfillment.get_subcondition_from_vk(testuser1_pub)[0]
subfulfillment_testuser2 = escrow_fulfillment.get_subcondition_from_vk(testuser2_pub)[0]
subfulfillment_timeout = escrow_fulfillment.subconditions[0]['body'].subconditions[1]['body']
subfulfillment_timeout_inverted = escrow_fulfillment.subconditions[1]['body'].subconditions[1]['body']

tx_escrow_abort_fulfillment_message = \
    util.get_fulfillment_message(tx_escrow_abort,
                                 tx_escrow_abort['transaction']['fulfillments'][0],
                                 serialized=True)
escrow_fulfillment.subconditions = []

# Do not fulfill execute branch
condition_execute = cc.ThresholdSha256Fulfillment(threshold=2)
condition_execute.add_subfulfillment(subfulfillment_testuser1)
condition_execute.add_subfulfillment(subfulfillment_timeout)
escrow_fulfillment.add_subcondition(condition_execute.condition)

# Fulfill abort branch
fulfillment_abort = cc.ThresholdSha256Fulfillment(threshold=2)
subfulfillment_testuser2.sign(tx_escrow_abort_fulfillment_message, crypto.SigningKey(testuser2_priv))
fulfillment_abort.add_subfulfillment(subfulfillment_testuser2)
fulfillment_abort.add_subfulfillment(subfulfillment_timeout_inverted)
escrow_fulfillment.add_subfulfillment(fulfillment_abort)

tx_escrow_abort['transaction']['fulfillments'][0]['fulfillment'] = escrow_fulfillment.serialize_uri()

for i in range(time_sleep - 4):
    valid_execute = b.is_valid_transaction(tx_escrow_execute) == tx_escrow_execute
    valid_abort = b.is_valid_transaction(tx_escrow_abort) == tx_escrow_abort

    seconds_to_timeout = int(float(time_expire) - float(gen_timestamp()))
    print('tx_execute valid: {} - tx_abort valid {} ({}s to timeout)'.format(valid_execute, valid_abort, seconds_to_timeout))
    sleep(1)
