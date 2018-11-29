
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _the-websocket-event-stream-api:

The WebSocket Event Stream API
==============================

.. important::
    The WebSocket Event Stream runs on a different port than the Web API. The
    default port for the Web API is `9984`, while the one for the Event Stream
    is `9985`.

BigchainDB provides real-time event streams over the WebSocket protocol with
the Event Stream API.
Connecting to an event stream from your application enables a BigchainDB node
to notify you as events occur, such as new `valid transactions <#valid-transactions>`_.


Demoing the API
---------------

You may be interested in demoing the Event Stream API with the `WebSocket echo test <http://websocket.org/echo.html>`_
to familiarize yourself before attempting an integration.


Determining Support for the Event Stream API
--------------------------------------------

It's a good idea to make sure that the node you're connecting with
has advertised support for the Event Stream API. To do so, send a HTTP GET
request to the node's :ref:`api-root-endpoint`
(e.g. ``http://localhost:9984/api/v1/``) and check that the
response contains a ``streams`` property:

.. code:: JSON

    {
     ...,
     "streams": "ws://example.com:9985/api/v1/streams/valid_transactions",
     ...
    }


Connection Keep-Alive
---------------------

The Event Stream API supports Ping/Pong frames as descibed in
`RFC 6455  <https://tools.ietf.org/html/rfc6455#section-5.5.2>`_.

.. note::

    It might not be possible to send PING/PONG frames via web browsers because
    of non availability of Javascript API on different browsers to achieve the
    same.

Streams
-------

Each stream is meant as a unidirectional communication channel, where the
BigchainDB node is the only party sending messages. Any messages sent to the
BigchainDB node will be ignored.

Streams will always be under the WebSocket protocol (so ``ws://`` or
``wss://``) and accessible as extensions to the ``/api/v<version>/streams/``
API root URL (for example, `valid transactions <#valid-transactions>`_
would be accessible under ``/api/v1/streams/valid_transactions``). If you're
running your own BigchainDB instance and need help determining its root URL,
then see the page titled :ref:`determining-the-api-root-url`.

All messages sent in a stream are in the JSON format.

.. note::

    For simplicity, BigchainDB initially only provides a stream for all
    committed transactions. In the future, we may provide streams for other
    information. We may
    also provide the ability to filter the stream for specific qualities, such
    as a specific ``output``'s ``public_key``.

    If you have specific use cases that you think would fit as part of this
    API, consider creating a new `BEP <https://github.com/bigchaindb/BEPs>`_.

Valid Transactions
~~~~~~~~~~~~~~~~~~

``/valid_transactions``

Streams an event for any newly valid transactions committed to a block. Message
bodies contain the transaction's ID, associated asset ID, and containing
block's height.

Example message:

.. code:: JSON

    {
        "transaction_id": "<sha3-256 hash>",
        "asset_id": "<sha3-256 hash>",
        "height": <int>
    }


.. note::

    Transactions in BigchainDB are committed in batches ("blocks") and will,
    therefore, be streamed in batches.
