# The Python Server API by Example

This section gives an example of using the Python Server API to interact _directly_ with a BigchainDB node running BigchainDB Server. That is, in this example, the Python code and BigchainDB Server run on the same machine.

(One can also interact with a BigchainDB node via other APIs, including the HTTP Client-Server API.) 

We create a digital asset, sign it, write it to a BigchainDB Server instance, read it, transfer it to a different user, and then attempt to transfer it to another user, resulting in a double-spend error.

## Getting Started

First, make sure you have RethinkDB and BigchainDB _installed and running_, i.e. you [installed them](installing-server.html) and you ran:
```text
$ rethinkdb
$ bigchaindb configure
$ bigchaindb init
$ bigchaindb start
```

Don't shut them down! In a new terminal, open a Python shell:
```text
$ python
```

Now we can import the `Bigchain` class and create an instance:
```python
from bigchaindb import Bigchain
b = Bigchain()
```

This instantiates an object `b` of class `Bigchain`. When instantiating a `Bigchain` object without arguments (as above), it reads the configurations stored in `$HOME/.bigchaindb`.

In a federation of BigchainDB nodes, each node has its own `Bigchain` instance.

The `Bigchain` class is the main API for all BigchainDB interactions, right now. It does things that BigchainDB nodes do, but it also does things that BigchainDB clients do. In the future, it will be broken apart into a node/server class and a client class.

The `Bigchain` class is documented in the [Developer Interface](developer-interface.html) section.

## Create a Digital Asset

At a high level, a "digital asset" is something which can be represented digitally and can be assigned to a user. In BigchainDB, users are identified by their public key, and the data payload in a digital asset is represented using a generic [Python dict](https://docs.python.org/3.4/tutorial/datastructures.html#dictionaries).

In BigchainDB, only the federation nodes are allowed to create digital assets, by doing a special kind of transaction: a `CREATE` transaction.

```python
from bigchaindb import crypto

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
```

## Read the Creation Transaction from the DB

After a couple of seconds, we can check if the transactions was included in the bigchain:
```python
# retrieve a transaction from the bigchain
tx_retrieved = b.get_transaction(tx_signed['id'])

{
    "id": "cdb6331f26ecec0ee7e67e4d5dcd63734e7f75bbd1ebe40699fc6d2960ae4cb2",
    "transaction": {
        "conditions": [
            {
                "cid": 0,
                "condition": {
                    "details": {
                        "bitmask": 32,
                        "public_key": "DTJCqP3sNkZcpoSA8bCtGwZ4ASfRLsMFXZDCmMHzCoeJ",
                        "signature": null,
                        "type": "fulfillment",
                        "type_id": 4
                    },
                    "uri": "cc:1:20:uQjL_E_uT1yUsJpVi1X7x2G7B15urzIlKN5fUufehTM:98"
                },
                "new_owners": [
                    "DTJCqP3sNkZcpoSA8bCtGwZ4ASfRLsMFXZDCmMHzCoeJ"
                ]
            }
        ],
        "data": {
            "hash": "872fa6e6f46246cd44afdb2ee9cfae0e72885fb0910e2bcf9a5a2a4eadb417b8",
            "payload": {
                "msg": "Hello BigchainDB!"
            }
        },
        "fulfillments": [
            {
                "current_owners": [
                    "3LQ5dTiddXymDhNzETB1rEkp4mA7fEV1Qeiu5ghHiJm9"
                ],
                "fid": 0,
                "fulfillment": "cf:1:4:ICKvgXHM8K2jNlKRfkwz3cCvH0OiF5A_-riWsQWXffOMQCyqbFgSDfKTaKRQHypHr5z5jsXzCQ4dKgYkmUo55CMxYs3TT2OxGiV0bZ7Tzn1lcLhpyutGZWm8xIyJKJmmSQQ",
                "input": null
            }
        ],
        "operation": "CREATE",
        "timestamp": "1460450439.267737"
    },
    "version": 1
}

```

The new owner of the digital asset is now `DTJCqP3sNkZcpoSA8bCtGwZ4ASfRLsMFXZDCmMHzCoeJ`, which is the public key of `testuser1`.

Note that the current owner with public key `3LQ5dTiddXymDhNzETB1rEkp4mA7fEV1Qeiu5ghHiJm9` refers to one of the federation nodes that actually created the asset and assigned it to `testuser1`.

## Transfer the Digital Asset

Now that `testuser1` has a digital asset assigned to him, he can transfer it to another user. Transfer transactions require an input. The input will be the transaction id of a digital asset that was assigned to `testuser1`, which in our case is `cdb6331f26ecec0ee7e67e4d5dcd63734e7f75bbd1ebe40699fc6d2960ae4cb2`.

Since a transaction can have multiple outputs with each their own (crypto)condition, each transaction input should also refer to the condition index `cid`.

```python
# create a second testuser
testuser2_priv, testuser2_pub = crypto.generate_key_pair()

# retrieve the transaction with condition id
tx_retrieved_id = b.get_owned_ids(testuser1_pub).pop()
    {'cid': 0,
     'txid': 'cdb6331f26ecec0ee7e67e4d5dcd63734e7f75bbd1ebe40699fc6d2960ae4cb2'}


# create a transfer transaction
tx_transfer = b.create_transaction(testuser1_pub, testuser2_pub, tx_retrieved_id, 'TRANSFER')

# sign the transaction
tx_transfer_signed = b.sign_transaction(tx_transfer, testuser1_priv)

# write the transaction
b.write_transaction(tx_transfer_signed)

# check if the transaction is already in the bigchain
tx_transfer_retrieved = b.get_transaction(tx_transfer_signed['id'])

{
    "id": "86ce10d653c69acf422a6d017a4ccd27168cdcdac99a49e4a38fb5e0d280c579",
    "transaction": {
        "conditions": [
            {
                "cid": 0,
                "condition": {
                    "details": {
                        "bitmask": 32,
                        "public_key": "7MUjLUFEu12Hk5jb8BZEFgM5JWgSya47SVbqzDqF6ZFQ",
                        "signature": null,
                        "type": "fulfillment",
                        "type_id": 4
                    },
                    "uri": "cc:1:20:XmUXkarmpe3n17ITJpi-EFy40qvGZ1C9aWphiiRfjOs:98"
                },
                "new_owners": [
                    "7MUjLUFEu12Hk5jb8BZEFgM5JWgSya47SVbqzDqF6ZFQ"
                ]
            }
        ],
        "data": null,
        "fulfillments": [
            {
                "current_owners": [
                    "DTJCqP3sNkZcpoSA8bCtGwZ4ASfRLsMFXZDCmMHzCoeJ"
                ],
                "fid": 0,
                "fulfillment": "cf:1:4:ILkIy_xP7k9clLCaVYtV-8dhuwdebq8yJSjeX1Ln3oUzQPKxMGutQV0EIRYxg81_Z6gdUHQYHkEyTKxwN7zRFjHNAnIdyU1NxqqohhFQSR-qYho-L-uqPRJcAed-SI7xwAI",
                "input": {
                    "cid": 0,
                    "txid": "cdb6331f26ecec0ee7e67e4d5dcd63734e7f75bbd1ebe40699fc6d2960ae4cb2"
                }
            }
        ],
        "operation": "TRANSFER",
        "timestamp": "1460450449.289641"
    },
    "version": 1
}

```

## Double Spends

BigchainDB makes sure that a user can't transfer the same digital asset two or more times (i.e. it prevents double spends).

If we try to create another transaction with the same input as before, the transaction will be marked invalid and the validation will throw a double spend exception:

```python
# create another transfer transaction with the same input
tx_transfer2 = b.create_transaction(testuser1_pub, testuser2_pub, tx_retrieved_id, 'TRANSFER')

# sign the transaction
tx_transfer_signed2 = b.sign_transaction(tx_transfer2, testuser1_priv)

# check if the transaction is valid
b.validate_transaction(tx_transfer_signed2)
DoubleSpend: input `cdb6331f26ecec0ee7e67e4d5dcd63734e7f75bbd1ebe40699fc6d2960ae4cb2` was already spent
```

## Crypto-Conditions

BigchainDB makes use of the crypto-conditions library to both cryptographically lock and unlock transactions.
The locking script is refered to as a `condition` and a corresponding `fulfillment` unlocks the condition of the `input_tx`. 

![BigchainDB transactions connecting fulfillments with conditions](./_static/tx_single_condition_single_fulfillment_v1.png)


### Introduction

Crypto-conditions provide a mechanism to describe a signed message such that multiple actors in a distributed system can all verify the same signed message and agree on whether it matches the description. 

This provides a useful primitive for event-based systems that are distributed on the Internet since we can describe events in a standard deterministic manner (represented by signed messages) and therefore define generic authenticated event handlers.

Crypto-conditions are part of the Interledger protocol and the full specification can be found [here](https://interledger.org/five-bells-condition/spec.html).

Implementations of the crypto-conditions are available in [Python](https://github.com/bigchaindb/cryptoconditions) and [JavaScript](https://github.com/interledger/five-bells-condition).


### Threshold Signatures

MultiSig, m-of-n signatures

```python
import copy
import json

from cryptoconditions import Ed25519Fulfillment, ThresholdSha256Fulfillment
from bigchaindb import util, crypto

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

# check if the transaction is already in the bigchain
tx_threshold_retrieved = b.get_transaction(threshold_tx_signed['id'])

{
    "id": "f0ea4a96afb3b8cafd6336aa3c4b44d1bb0f2b801f61fcb6a44eea4b870ff2e2",
    "transaction": {
        "conditions": [
            {
                "cid": 0,
                "condition": {
                    "details": {
                        "bitmask": 41,
                        "subfulfillments": [
                            {
                                "bitmask": 32,
                                "public_key": "3tuSZ4FitNVWRgK7bGe6pEia7ERmxHmhCxFfFEVbD7g4",
                                "signature": null,
                                "type": "fulfillment",
                                "type_id": 4,
                                "weight": 1
                            },
                            {
                                "bitmask": 32,
                                "public_key": "8CvrriTsPZULEXTZW2Hnmg7najZsvXzgTi9NKpJaUdHS",
                                "signature": null,
                                "type": "fulfillment",
                                "type_id": 4,
                                "weight": 1
                            }
                        ],
                        "threshold": 2,
                        "type": "fulfillment",
                        "type_id": 2
                    },
                    "uri": "cc:1:29:kiQHpdEiRe24L62KzwQgLu7dxCHaLBfEFLr_xzlswT4:208"
                },
                "new_owners": [
                    "3tuSZ4FitNVWRgK7bGe6pEia7ERmxHmhCxFfFEVbD7g4",
                    "8CvrriTsPZULEXTZW2Hnmg7najZsvXzgTi9NKpJaUdHS"
                ]
            }
        ],
        "data": null,
        "fulfillments": [
            {
                "current_owners": [
                    "7MUjLUFEu12Hk5jb8BZEFgM5JWgSya47SVbqzDqF6ZFQ"
                ],
                "fid": 0,
                "fulfillment": "cf:1:4:IF5lF5Gq5qXt59eyEyaYvhBcuNKrxmdQvWlqYYokX4zrQDSWz8yxBCFaYFKZOLai5ZCoVq28LVoiQ7TL5zkajG-I-BYH2NaKj7CfPBIZHWkMGWfd_UuQWkbhyx07MJ_1Jww",
                "input": {
                    "cid": 0,
                    "txid": "86ce10d653c69acf422a6d017a4ccd27168cdcdac99a49e4a38fb5e0d280c579"
                }
            }
        ],
        "operation": "TRANSFER",
        "timestamp": "1460450459.321600"
    },
    "version": 1
}

```

```python
from cryptoconditions.fulfillment import Fulfillment

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

b.write_transaction(threshold_tx_transfer)

{
    "id": "27d1e780526e172fdafb6cfec24b43878b0f8a2c34e962546ba4932ef7662646",
    "transaction": {
        "conditions": [
            {
                "cid": 0,
                "condition": {
                    "details": {
                        "bitmask": 32,
                        "public_key": "4SwVNiYRykGw1ixgKH75k97ipCnmm5QpwNwzQdCKLCzH",
                        "signature": null,
                        "type": "fulfillment",
                        "type_id": 4
                    },
                    "uri": "cc:1:20:MzgxMS8Zt2XZrSA_dFk1d64nwUz16knOeKkxc5LyIv4:98"
                },
                "new_owners": [
                    "4SwVNiYRykGw1ixgKH75k97ipCnmm5QpwNwzQdCKLCzH"
                ]
            }
        ],
        "data": null,
        "fulfillments": [
            {
                "current_owners": [
                    "3tuSZ4FitNVWRgK7bGe6pEia7ERmxHmhCxFfFEVbD7g4",
                    "8CvrriTsPZULEXTZW2Hnmg7najZsvXzgTi9NKpJaUdHS"
                ],
                "fid": 0,
                "fulfillment": "cf:1:2:AgIBYwQgKwNKM5oJUhL3lUJ3Xj0dzePTH_1BOxcIry5trRxnNXFANabre0P23pzs3liGozZ-cua3zLZuZIc4UA-2Eb_3oi0zFZKHlL6_PrfxpZFp4Mafsl3Iz1yGVz8s-x5jcbahDwABYwQgaxAYvRMOihIk-M4AZYFB2mlf4XjEqhiOaWpqinOYiXFAuQm7AMeXDs4NCeFI4P6YeL3RqNZqyTr9OsNHZ9JgJLZ2ER1nFpwsLhOt4TJZ01Plon7r7xA2GFKFkw511bRWAQA",
                "input": {
                    "cid": 0,
                    "txid": "f0ea4a96afb3b8cafd6336aa3c4b44d1bb0f2b801f61fcb6a44eea4b870ff2e2"
                }
            }
        ],
        "operation": "TRANSFER",
        "timestamp": "1460450469.337543"
    },
    "version": 1
}

```


### Merkle Trees
