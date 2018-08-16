
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _the-block-model:

The Block Model
===============

A block is a JSON object with a particular schema,
as outlined in this page.
A block must contain the following JSON keys
(also called names or fields):

.. code-block:: json

    {
      "height": "<Height of the block>",
      "transactions": ["<List of transactions>"]
    }


The JSON Keys in a Block
------------------------

**height**

The block ``"height"`` (``integer``) denotes the height of the blockchain when the given block was committed.
Since the blockchain height increases monotonically the height of block can be regarded as its id.

**NOTE**: The genesis block has height ``0``


**transactions**

A list of the :ref:`transactions <the-transaction-model>` included in the block.
(Each transaction is a JSON object.)
