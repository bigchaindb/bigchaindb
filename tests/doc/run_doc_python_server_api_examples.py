import copy
import json
from time import sleep

from cryptoconditions import Ed25519Fulfillment, ThresholdSha256Fulfillment
from cryptoconditions.fulfillment import Fulfillment

from bigchaindb import Bigchain, util, crypto, exceptions


b = Bigchain()

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

tx_retrieved = b.get_transaction(tx_signed['id'])

# create a second testuser
testuser2_priv, testuser2_pub = crypto.generate_key_pair()

# retrieve the transaction with condition id
tx_retrieved_id = b.get_owned_ids(testuser1_pub).pop()

# create a transfer transaction
tx_transfer = b.create_transaction(testuser1_pub, testuser2_pub, tx_retrieved_id, 'TRANSFER')

# sign the transaction
tx_transfer_signed = b.sign_transaction(tx_transfer, testuser1_priv)

# write the transaction
b.write_transaction(tx_transfer_signed)

sleep(10)

# check if the transaction is already in the bigchain
tx_transfer_retrieved = b.get_transaction(tx_transfer_signed['id'])

# create another transfer transaction with the same input
tx_transfer2 = b.create_transaction(testuser1_pub, testuser2_pub, tx_retrieved_id, 'TRANSFER')

# sign the transaction
tx_transfer_signed2 = b.sign_transaction(tx_transfer2, testuser1_priv)

# check if the transaction is valid
try:
    b.validate_transaction(tx_transfer_signed2)
except exceptions.DoubleSpend as e:
    print(e)

# create some new testusers
thresholduser1_priv, thresholduser1_pub = crypto.generate_key_pair()
thresholduser2_priv, thresholduser2_pub = crypto.generate_key_pair()

# retrieve the last transaction of testuser2
tx_retrieved_id = b.get_owned_ids(testuser2_pub).pop()

# create a base template for a 1-input/2-output transaction
threshold_tx = b.create_transaction(testuser2_pub, [thresholduser1_pub, thresholduser2_pub], tx_retrieved_id, 'TRANSFER')

# create a Threshold Cryptocondition
threshold_condition = ThresholdSha256Fulfillment(threshold=2)
threshold_condition.add_subfulfillment(Ed25519Fulfillment(public_key=thresholduser1_pub))
threshold_condition.add_subfulfillment(Ed25519Fulfillment(public_key=thresholduser2_pub))

# update the condition in the newly created transaction
threshold_tx['transaction']['conditions'][0]['condition'] = {
    'details': json.loads(threshold_condition.serialize_json()),
    'uri': threshold_condition.condition.serialize_uri()
}

# conditions have been updated, so hash needs updating
threshold_tx_data = copy.deepcopy(threshold_tx)
for fulfillment in threshold_tx_data['transaction']['fulfillments']:
    fulfillment['fulfillment'] = None

threshold_tx['id'] = crypto.hash_data(util.serialize(threshold_tx_data['transaction']))

# sign the transaction
threshold_tx_signed = b.sign_transaction(threshold_tx, testuser2_priv)

# write the transaction
b.write_transaction(threshold_tx_signed)

sleep(10)

# check if the transaction is already in the bigchain
tx_threshold_retrieved = b.get_transaction(threshold_tx_signed['id'])

thresholduser3_priv, thresholduser3_pub = crypto.generate_key_pair()

# retrieve the last transaction of thresholduser1_pub
tx_retrieved_id = b.get_owned_ids(thresholduser1_pub).pop()

# create a base template for a 2-input/1-output transaction
threshold_tx_transfer = b.create_transaction([thresholduser1_pub, thresholduser2_pub], thresholduser3_pub, tx_retrieved_id, 'TRANSFER')

# parse the threshold cryptocondition
threshold_fulfillment = Fulfillment.from_json(threshold_tx['transaction']['conditions'][0]['condition']['details'])
subfulfillment1 = threshold_fulfillment.subconditions[0]['body']
subfulfillment2 = threshold_fulfillment.subconditions[1]['body']

# get the fulfillment message to sign
threshold_tx_fulfillment_message = util.get_fulfillment_message(threshold_tx_transfer,
                                                                threshold_tx_transfer['transaction']['fulfillments'][0])

# sign the subconditions
subfulfillment1.sign(util.serialize(threshold_tx_fulfillment_message), crypto.SigningKey(thresholduser1_priv))
subfulfillment2.sign(util.serialize(threshold_tx_fulfillment_message), crypto.SigningKey(thresholduser2_priv))

threshold_tx_transfer['transaction']['fulfillments'][0]['fulfillment'] = threshold_fulfillment.serialize_uri()

b.verify_signature(threshold_tx_transfer)

b.validate_transaction(threshold_tx_transfer)

b.write_transaction(threshold_tx_transfer)

