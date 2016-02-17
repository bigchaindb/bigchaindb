# Getting Started (Tutorial)

This section gives an example of using BigchainDB. We create a digital asset, sign it, write it to a BigchainDB instance, read it, transfer it to a different user, and then attempt to transfer it to another user, resulting in a double-spend error.

## Getting Going

First, make sure you have RethinkDB and BigchainDB _installed and running_, i.e. you [installed them](installing.html) and you ran:
```text
$ rethinkdb
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
# create a test user
testuser1_priv, testuser1_pub = b.generate_keys()

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

   'id': '6539dded9479c47b3c83385ae569ecaa90bcf387240d1ee2ea3ae0f7986aeddd',
   'transaction': {   'current_owner': 'pvGtcm5dvwWMzCqagki1N6CDKYs2J1cCwTNw8CqJic3Q',
                      'data': {   'hash': '872fa6e6f46246cd44afdb2ee9cfae0e72885fb0910e2bcf9a5a2a4eadb417b8',
                                  'payload': {'msg': 'Hello BigchainDB!'}},
                      'input': None,
                      'new_owner': 'ssQnnjketNYmbU3hwgFMEQsc4JVYAmZyWHnHCtFS8aeA',
                      'operation': 'CREATE',
                      'timestamp': '1455108421.753908'}}
```

The new owner of the digital asset is now `ssQnnjketNYmbU3hwgFMEQsc4JVYAmZyWHnHCtFS8aeA`, which is the public key of `testuser1`.

## Transfer the Digital Asset

Now that `testuser1` has a digital asset assigned to him, he can transfer it to another user. Transfer transactions require an input. The input will be the transaction id of a digital asset that was assigned to `testuser1`, which in our case is `6539dded9479c47b3c83385ae569ecaa90bcf387240d1ee2ea3ae0f7986aeddd`.

```python
# create a second testuser
testuser2_priv, testuser2_pub = b.generate_keys()

# create a transfer transaction
tx_transfer = b.create_transaction(testuser1_pub, testuser2_pub, tx_retrieved['id'], 'TRANSFER')

# sign the transaction
tx_transfer_signed = b.sign_transaction(tx_transfer, testuser1_priv)

# write the transaction
b.write_transaction(tx_transfer_signed)

# check if the transaction is already in the bigchain
tx_transfer_retrieved = b.get_transaction(tx_transfer_signed['id'])

{   'id': '1b78c313257540189f27da480152ed8c0b758569cdadd123d9810c057da408c3',
    'signature': '3045022056166de447001db8ef024cfa1eecdba4306f92688920ac24325729d5a5068d47022100fbd495077cb1040c48bd7dc050b2515b296ca215cb5ce3369f094928e31955f6',
    'transaction': {   'current_owner': 'ssQnnjketNYmbU3hwgFMEQsc4JVYAmZyWHnHCtFS8aeA',
                       'data': None,
                       'input': '6539dded9479c47b3c83385ae569ecaa90bcf387240d1ee2ea3ae0f7986aeddd',
                       'new_owner': 'zVzophT73m4Wvf3f8gFYokddkYe3b9PbaMzobiUK7fmP',
                       'operation': 'TRANSFER',
                       'timestamp': '1455109497.480323'}}
```

## Double Spends

BigchainDB makes sure that a user can't transfer the same digital asset two or more times (i.e. it prevents double spends).

If we try to create another transaction with the same input as before, the transaction will be marked invalid and the validation will throw a double spend exception:

```python
# create another transfer transaction with the same input
tx_transfer2 = b.create_transaction(testuser1_pub, testuser2_pub, tx_retrieved['id'], 'TRANSFER')

# sign the transaction
tx_transfer_signed2 = b.sign_transaction(tx_transfer2, testuser1_priv)

# check if the transaction is valid
b.validate_transaction(tx_transfer_signed2)
Exception: input `6539dded9479c47b3c83385ae569ecaa90bcf387240d1ee2ea3ae0f7986aeddd` was already spent
```
