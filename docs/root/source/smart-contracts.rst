BigchainDB and Smart Contracts
==============================

One can store the source code of any smart contract (i.e. a computer program) in BigchainDB, but BigchainDB won't run arbitrary smart contracts.

BigchainDB will run the subset of smart contracts expressible using `Crypto-Conditions <https://tools.ietf.org/html/draft-thomas-crypto-conditions-03>`_. Crypto-conditions are part of the `Interledger Protocol <https://interledger.org/>`_.

The owners of an asset can impose conditions on it that must be met for the asset to be transferred to new owners. Examples of possible conditions (crypto-conditions) include:

- The current owner must sign the transfer transaction (one which transfers ownership to new owners).
- Three out of five current owners must sign the transfer transaction.
- (Shannon and Kelly) or Morgan must sign the transfer transaction.

Crypto-conditions can be quite complex. They can't include loops or recursion and therefore will always run/check in finite time.

.. note::

   We used the word "owners" somewhat loosely above. A more accurate word might be fulfillers, signers, controllers, or transfer-enablers. See the section titled **A Note about Owners** in the relevant `BigchainDB Transactions Spec <https://github.com/bigchaindb/BEPs/tree/master/tx-specs/>`_.