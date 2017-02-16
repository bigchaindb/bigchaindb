The WebSocket Event Stream API
==============================

.. important::
    This is currently scheduled to be implemented in BigchainDB Server 0.10.

BigchainDB provides real-time event streams over the WebSocket protocol with
the Event Stream API.

Connecting to an event stream from your application enables a BigchainDB node
to notify you as events are processed, such as new `validated transactions <#valid-transactions>`_.


Demoing the API
---------------

You may be interested in demoing the Event Stream API with the `WebSocket echo test <http://websocket.org/echo.html>`_
to familiarize yourself before attempting an integration.


Determining Support for the Event Stream API
--------------------------------------------

In practice, it's a good idea to make sure that the node you're connecting with
has advertised support for the Event Stream API. To do so, send a HTTP GET
request to the node's :ref:`Root URL <bigchaindb-root-url>` and check that the
response contains a ``streams_<version>`` property in ``_links``::

    {
      "_links": {
         "streams_v1": "ws://example.com:9984/api/v1/streams/"
      }
    }


Connection Keep Alive
~~~~~~~~~~~~~~~~~~~~~

The Event Stream API initially does not provide any mechanisms for connection
keep alive other than enabling TCP keepalive on each open WebSocket connection.
In the future, we may add additional functionality to handle ping/pong frames
or payloads designed for keep alive.

Streams
-------

Each stream is meant as a unidirectional communication channel, where the
BigchainDB node is the only party sending messages. Any messages sent to the
BigchainDB node will be ignored.

Streams will always be under the WebSocket protocol (so ``ws://`` or
``wss://``) and accessible as extensions to the ``/api/v<version>/streams/``
API root URL (for example, `validated transactions <#valid-transactions>`_
would be accessible under ``/api/v1/streams/valid_tx``). If you're running your
own BigchainDB instance and need help determining its root URL, you can find
more :ref:`here <determining-the-api-root-url>`.

All messages sent in a stream are in the JSON format.

.. note::

    For simplicity, BigchainDB initially only provides a stream for all
    validated transactions. In the future, we may provide streams for other
    information, such as new blocks, new votes, or invalid transactions. We may
    also provide the ability to filter the stream for specific qualities, such
    as a specific ``output``'s ``public_key``.

    If you have specific use cases that you think would fit as part of this
    API, feel free to reach out via `gitter <https://gitter.im/bigchaindb/bigchaindb>`_
    or `email <mailto:product@bigchaindb.com>`_.

Valid Transactions
~~~~~~~~~~~~~~~~~~

``/valid_tx``

Streams an event for any newly validated transactions. Message bodies contain
the transaction's ID, associated asset ID, and containing block's ID.

Example message::

    {
        "txid": "<sha3-256 hash>",
        "assetid": "<sha3-256 hash>",
        "blockid": "<sha3-256 hash>"
    }


.. note::

    Transactions in BigchainDB are validated in batches ("blocks") and will,
    therefore, be streamed in batches. Each block can contain up to a 1000
    transactions, ordered by the time at which they were included in the block.
    The ``/valid_tx`` stream will send these transactions in the same order
    that the block stored them in, but this does **NOT** guarantee that you
    will recieve the events in that same order.
