# Transaction Concepts

In BigchainDB, _Transactions_ are used to register, issue, create or transfer things (e.g. assets).

Transactions are the most basic kind of record stored by BigchainDB. There are two kinds: creation transactions and transfer transactions.

A _creation transaction_ can be used to register, issue, create or otherwise initiate the history of a single thing (or asset) in BigchainDB. For example, one might register an identity or a creative work. The things are often called "assets" but they might not be literal assets.

Currently, BigchainDB only supports indivisible assets. You can't split an asset apart into multiple assets, nor can you combine several assets together into one. [Issue #129](https://github.com/bigchaindb/bigchaindb/issues/129) is an enhancement proposal to support divisible assets.

A creation transaction also establishes the conditions that must be met to transfer the asset. For example, there may be a condition that any transfer must be signed (cryptographically) by the signing/private key associated with a given verifying/public key. More sophisticated conditions are possible. BigchainDB's conditions are based on the crypto-conditions of the [Interledger Protocol (ILP)](https://interledger.org/).

A _transfer transaction_ can transfer an asset by fulfilling the current conditions on the asset. It can also specify new transfer conditions.

Today, every transaction contains one fulfillment-condition pair. The fulfillment in a transfer transaction must fulfill a condition in a previous transaction.

When a node is asked to check if a transaction is valid, it checks several things. Some things it checks are:

* Are all the fulfillments valid? (Do they correctly satisfy the conditions they claim to satisfy?)
* If it's a creation transaction, is the asset valid?
* If it's a transfer transaction:
   * Is it trying to fulfill a condition in a nonexistent transaction?
   * Is it trying to fulfill a condition that's not in a valid transaction? (It's okay if the condition is in a transaction in an invalid block; those transactions are ignored. Transactions in the backlog or undecided blocks are not ignored.)
   * Is it trying to fulfill a condition that has already been fulfilled, or that some other pending transaction (in the backlog or an undecided block) also aims to fulfill?
   * Is the asset ID in the transaction the same as the asset ID in all transactions whose conditions are being fulfilled?

If you're curious about the details of transaction validation, the code is in the `validate` method of the `Transaction` class, in `bigchaindb/models.py` (at the time of writing).

Note: The check to see if the transaction ID is equal to the hash of the transaction body is actually done whenever the transaction is converted from a Python dict to a Transaction object, which must be done before the `validate` method can be called (since it's called on a Transaction object).
