The Block Model
===============

A block is a JSON object with a particular schema,
as outlined in this page.
A block must contain the following JSON keys
(also called names or fields):

.. code-block:: json

    {
      "id": "<ID of the block>",
      "transactions": ["<List of transactions>"]
    }


The JSON Keys in a Block
------------------------

**id**

The block ID denotes the height of the blockchain when the given block was committed.


**transactions**

A list of the :ref:`transactions <The Transaction Model>` included in the block.
(Each transaction is a JSON object.)
