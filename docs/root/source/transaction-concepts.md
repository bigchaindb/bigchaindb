# Transaction Concepts

In BigchainDB, _Transactions_ are used to register, issue, create or transfer things (e.g. assets).

Transactions are the most basic kind of record stored by BigchainDB. There are two kinds: creation transactions and transfer transactions.

A _creation transaction_ can be used to register, issue, create or otherwise initiate the history of a single thing (or asset) in BigchainDB. For example, one might register an identity or a creative work. The things are often called "assets" but they might not be literal assets.

Currently, BigchainDB only supports indivisible assets. You can't split an asset apart into multiple assets, nor can you combine several assets together into one. [Issue #129](https://github.com/bigchaindb/bigchaindb/issues/129) is an enhancement proposal to support divisible assets.

A creation transaction also establishes the conditions that must be met to transfer the asset. For example, there may be a condition that any transfer must be signed (cryptographically) by the signing/private key associated with a given verifying/public key. More sophisticated conditions are possible. BigchainDB's conditions are based on the crypto-conditions of the [Interledger Protocol (ILP)](https://interledger.org/).

A _transfer transaction_ can transfer an asset by fulfilling the current conditions on the asset. It can also specify new transfer conditions.

Today, every transaction contains one fulfillment-condition pair. The fulfillment in a transfer transaction must correspond to a condition in a previous transaction.

When a node is asked to check the validity of a transaction, it must do several things, including:

* double-spending checks (for transfer transactions),
* hash validation (i.e. is the calculated transaction hash equal to its id?), and
* validation of all fulfillments, including validation of cryptographic signatures if they’re among the conditions.

