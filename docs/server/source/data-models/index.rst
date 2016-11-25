Data Models
===========

BigchainDB stores all data in the underlying database as JSON documents (conceptually, at least). There are three main kinds:

1. Transactions, which contain digital assets, conditions, fulfillments and other things
2. Blocks
3. Votes

This section unpacks each one in turn.

.. toctree::
   :maxdepth: 1

   transaction-model 
   asset-model
   crypto-conditions
   block-model
   The Vote Model <../schema/vote>
