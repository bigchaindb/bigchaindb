BigchainDB and Smart Contracts
==============================

One can store the source code of any smart contract (i.e. a computer program) in BigchainDB, but BigchainDB won't run arbitrary smart contracts.

BigchainDB will run the subset of smart contracts expressible using "crypto-conditions," a subset we like to call "simple contracts." Crypto-conditions are part of the `Interledger Protocol <https://interledger.org/>`_.

The owners of an asset can impose conditions on it that must be met for the asset to be transferred to new owners. Examples of possible conditions (crypto-conditions) include:

- The current owner must sign the transfer transaction (one which transfers ownership to new owners).
- Three out of five current owners must sign the transfer transaction.
- (Shannon and Kelly) or Morgan must sign the transfer transaction.

Crypto-conditions can be quite complex if-this-then-that type conditions, where the "this" can be a long boolean expression. Crypto-conditions can't include loops or recursion and are therefore will always run/check in finite time.

.. note::

   We used the word "owners" somewhat loosely above. A more accurate word might be fulfillers, signers, controllers, or tranfer-enablers. See BigchainDB Server `issue #626 <https://github.com/bigchaindb/bigchaindb/issues/626>`_.
   