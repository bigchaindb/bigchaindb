.. raw:: html

   <style>
    .rst-content a.internal[href*='/schema/'] {
        border: solid 1px #e1e4e5;
        font-family: monospace;
        font-size: 12px;
        color: blue;
        padding: 2px 4px;
        background-color: white;
    }
   </style>

=====================
The Transaction Model
=====================

A transaction has the following structure:

.. code-block:: json

    {
        "id": "<hash of transaction, excluding signatures (see explanation)>",
        "version": "<version number of the transaction model>",
        "inputs": ["<list of inputs>"],
        "outputs": ["<list of outputs>"],
        "operation": "<string>",
        "asset": "<asset model; see below>",
        "metadata": "<any JSON document>"
    }

Here's some explanation of the contents of a :ref:`transaction <transaction>`:

- **id**: The :ref:`id <transaction.id>` of the transaction, and also the database primary key.

- **version**: :ref:`Version <transaction.version>` number of the transaction model, so that software can support different transaction models.

- **inputs**: List of inputs. Each :ref:`input <Input>` contains a pointer to an unspent output
  and a *crypto fulfillment* that satisfies the conditions of that output. A *fulfillment*
  is usually a signature proving the ownership of the asset.
  See :doc:`./inputs-outputs`.

- **outputs**: List of outputs. Each :ref:`output <Output>` contains *crypto-conditions* that need to be fulfilled by a transfer transaction in order to transfer ownership to new owners.
  See :doc:`./inputs-outputs`.

- **operation**: String representation of the :ref:`operation <transaction.operation>` being performed (currently either "CREATE", "TRANSFER" or "GENESIS"). It determines how the transaction should be validated.

- **asset**: Definition of the :ref:`asset <Asset>`. See :ref:`the page about the asset model <The Asset Model>`.

- **metadata**: User-provided transaction :ref:`metadata <metadata>`: Can be any JSON document, or `NULL`.

Later, when we get to the models for the block and the vote, we'll see that both include a signature (from the node which created it). You may wonder why transactions don't have signatures... The answer is that they do! They're just hidden inside the ``fulfillment`` string of each input. A creation transaction is signed by whoever created it. A transfer transaction is signed by whoever currently controls or owns it.

What gets signed? For each input in the transaction, the "fullfillment message" that gets signed includes the JSON serialized body of the transaction, minus any fulfillment strings. The computed signature goes into creating the ``fulfillment`` string of the input.
