
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

How BigchainDB is Good for Asset Registrations & Transfers
==========================================================

BigchainDB can store data of any kind (within reason), but it's designed to be particularly good for storing asset registrations and transfers:

* The fundamental thing that one sends to a BigchainDB network, to be checked and stored (if valid), is a *transaction*, and there are two kinds: CREATE transactions and TRANSFER transactions.
* A CREATE transaction can be use to register any kind of asset (divisible or indivisible), along with arbitrary metadata.
* An asset can have zero, one, or several owners.
* The owners of an asset can specify (crypto-)conditions which must be satisfied by anyone wishing transfer the asset to new owners. For example, a condition might be that at least 3 of the 5 current owners must cryptographically sign a TRANSFER transaction.
* BigchainDB verifies that the conditions have been satisfied as part of checking the validity of TRANSFER transactions. (Moreover, anyone can check that they were satisfied.)
* BigchainDB prevents double-spending of an asset.
* Validated transactions are :doc:`"immutable" <immutable>`.

.. note::

   We used the word "owners" somewhat loosely above. A more accurate word might be fulfillers, signers, controllers, or transfer-enablers. See the section titled **A Note about Owners** in the relevant `BigchainDB Transactions Spec <https://github.com/bigchaindb/BEPs/tree/master/tx-specs/>`_.