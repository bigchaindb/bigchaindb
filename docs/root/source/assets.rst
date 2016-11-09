How BigchainDB is Good for Asset Registrations & Transfers
==========================================================

BigchainDB can store data of any kind (within reason), but it's designed to be particularly good for storing asset registrations and transfers:

* The fundamental thing that one submits to a BigchainDB federation to be checked and stored (if valid) is a *transaction*, and there are two kinds: creation transactions and transfer transactions.
* A creation transaction can be use to register any kind of indivisible asset, along with arbitrary metadata.
* An asset can have zero, one, or several owners.
* The owners of an asset can specify (crypto-)conditions which must be satisified by anyone wishing transfer the asset to new owners. For example, a condition might be that at least 3 of the 5 current owners must cryptographically sign a transfer transaction.
* BigchainDB verifies that the conditions have been satisified as part of checking the validity of transfer transactions. (Moreover, anyone can check that they were satisfied.)
* BigchainDB prevents double-spending of an asset.
* Validated transactions are strongly tamper-resistant; see [the section about immutability / tamper-resistance](immutable.html).


BigchainDB Integration with Other Blockchains
---------------------------------------------

BigchainDB works with the `Interledger protocol <https://interledger.org/>`_, enabling the transfer of assets between BigchainDB and other blockchains, ledgers, and payment systems.

We’re actively exploring ways that BigchainDB can be used with other blockchains and platforms.

.. note::

   We used the word "owners" somewhat loosely above. A more accurate word might be fulfillers, signers, controllers, or tranfer-enablers. See BigchainDB Server `issue #626 <https://github.com/bigchaindb/bigchaindb/issues/626>`_.
