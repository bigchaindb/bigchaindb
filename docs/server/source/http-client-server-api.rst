
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _the-http-client-server-api:

The HTTP Client-Server API
==========================

This page assumes you already know an API Root URL
for a BigchainDB node or reverse proxy.
It should be something like ``https://example.com:9984``
or ``https://12.34.56.78:9984``.

If you set up a BigchainDB node or reverse proxy yourself,
and you're not sure what the API Root URL is,
then see the last section of this page for help.

.. _bigchaindb-root-url:

BigchainDB Root URL
-------------------

If you send an HTTP GET request to the BigchainDB Root URL
e.g. ``http://localhost:9984``
or ``https://example.com:9984``
(with no ``/api/v1/`` on the end),
then you should get an HTTP response
with something like the following in the body:

.. literalinclude:: http-samples/index-response.http
    :language: http


.. _api-root-endpoint:

API Root Endpoint
-----------------

If you send an HTTP GET request to the API Root Endpoint
e.g. ``http://localhost:9984/api/v1/``
or ``https://example.com:9984/api/v1/``,
then you should get an HTTP response
that allows you to discover the BigchainDB API endpoints:

.. literalinclude:: http-samples/api-index-response.http
    :language: http


Transactions
------------

.. note::

   If you want to do more sophisticated queries
   than those provided by the BigchainDB HTTP API,
   then one option is to connect to MongoDB directly (if possible)
   and do whatever queries MongoDB allows.
   For more about that option, see
   `the page about querying BigchainDB <https://docs.bigchaindb.com/en/latest/query.html>`_.

.. http:get:: /api/v1/transactions/{transaction_id}

   Get the transaction with the ID ``transaction_id``.

   If a transaction with ID ``transaction_id`` has been included
   in a committed block, then this endpoint returns that transaction,
   otherwise the response will be ``404 Not Found``.

   :param transaction_id: transaction ID
   :type transaction_id: hex string

   **Example request**:

   .. literalinclude:: http-samples/get-tx-id-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-tx-id-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A transaction with that ID was found.
   :statuscode 404: A transaction with that ID was not found.

.. http:get:: /api/v1/transactions

   Requests to the ``/api/v1/transactions`` endpoint
   without any query parameters will get a response status code ``400 Bad Request``.

.. http:get:: /api/v1/transactions?asset_id={asset_id}&operation={CREATE|TRANSFER}&last_tx={true|false}

   Get a list of transactions that use an asset with the ID ``asset_id``.

   If ``operation`` is ``CREATE``, then the CREATE transaction which created
   the asset with ID ``asset_id`` will be returned.

   If ``operation`` is ``TRANSFER``, then every TRANSFER transaction involving
   the asset with ID ``asset_id`` will be returned.
   This allows users to query the entire history or
   provenance of an asset.

   If ``operation`` is not included, then *every* transaction involving
   the asset with ID ``asset_id`` will be returned.

   if ``last_tx`` is set to ``true``, only the last transaction is returned
   instead of all transactions with the given ``asset_id``.

   This endpoint returns transactions only if they are in committed blocks.

   :query string operation: (Optional) ``CREATE`` or ``TRANSFER``.

   :query string asset_id: asset ID.

   :query string last_tx: (Optional) ``true`` or ``false``.


   **Example request**:

   .. literalinclude:: http-samples/get-tx-by-asset-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-tx-by-asset-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of transactions containing an asset with ID ``asset_id`` was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``asset_id`` querystring was not included in the request.


.. http:post:: /api/v1/transactions?mode={mode}

   This endpoint is used to send a transaction to a BigchainDB network.
   The transaction is put in the body of the request.

   :query string mode: (Optional) One of the three supported modes to send a transaction: ``async``, ``sync``, ``commit``. The default is ``async``.

   Once the posted transaction arrives at a BigchainDB node,
   that node will check to see if the transaction is valid.
   If it's invalid, the node will return an HTTP 400 (error).
   Otherwise, the node will send the transaction to Tendermint (in the same node) using the
   `Tendermint broadcast API
   <https://tendermint.com/docs/tendermint-core/using-tendermint.html#broadcast-api>`_.

   The meaning of the ``mode`` query parameter is inherited from the mode parameter in
   `Tendermint's broadcast API
   <https://tendermint.com/docs/tendermint-core/using-tendermint.html#broadcast-api>`_.
   ``mode=async`` means the HTTP response will come back immediately,
   before Tendermint asks BigchainDB Server to check the validity of the transaction (a second time).
   ``mode=sync`` means the HTTP response will come back
   after Tendermint gets a response from BigchainDB Server
   regarding the validity of the transaction.
   ``mode=commit`` means the HTTP response will come back once the transaction
   is in a committed block.

   .. note::
       In the async and sync modes, after a successful HTTP response is returned, the transaction may still be rejected later on. All the transactions are recorded internally by Tendermint in WAL (Write-Ahead Log) before the HTTP response is returned. Nevertheless, the following should be noted:

       - Transactions in WAL including the failed ones are not exposed in any of the BigchainDB or Tendermint APIs.
       - Transactions are never fetched from WAL. WAL is never replayed.
       - A critical failure (e.g. the system is out of disk space) may occur preventing transactions from being stored in WAL, even when the HTTP response indicates a success.
       - If a transaction fails the validation because it conflicts with the other transactions of the same block, Tendermint includes it into its block, but BigchainDB does not store these transactions and does not offer any information about them in the APIs.

   .. note::

       The posted transaction should be valid.
       The relevant
       `BigchainDB Transactions Spec <https://github.com/bigchaindb/BEPs/tree/master/tx-specs/>`_
       explains how to build a valid transaction
       and how to check if a transaction is valid.
       One would normally use a driver such as the `BigchainDB Python Driver
       <https://docs.bigchaindb.com/projects/py-driver/en/latest/index.html>`_
       to build a valid transaction.

   .. note::

       A client can subscribe to the
       WebSocket Event Stream API
       to listen for committed transactions.

   **Example request**:

   .. literalinclude:: http-samples/post-tx-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/post-tx-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 202: The meaning of this response depends on the value
                    of the ``mode`` parameter. See above.

   :statuscode 400: The posted transaction was invalid.


.. http:post:: /api/v1/transactions

   This endpoint (without any parameters) will push a new transaction.
   Since no ``mode`` parameter is included, the default mode is assumed: ``async``.


Transaction Outputs
-------------------

The ``/api/v1/outputs`` endpoint returns transactions outputs filtered by a
given public key, and optionally filtered to only include either spent or
unspent outputs.

.. note::

   If you want to do more sophisticated queries
   than those provided by the BigchainDB HTTP API,
   then one option is to connect to MongoDB directly (if possible)
   and do whatever queries MongoDB allows.
   For more about that option, see
   `the page about querying BigchainDB <https://docs.bigchaindb.com/en/latest/query.html>`_.

.. http:get:: /api/v1/outputs

   Get transaction outputs by public key. The ``public_key`` parameter must be
   a base58 encoded ed25519 public key associated with transaction output
   ownership.

   Returns a list of transaction outputs.

   :param public_key: Base58 encoded public key associated with output
                      ownership. This parameter is mandatory and without it
                      the endpoint will return a ``400`` response code.
   :param spent: (Optional) Boolean value (``true`` or ``false``)
                 indicating if the result set
                 should include only spent or only unspent outputs. If not
                 specified, the result includes all the outputs (both spent
                 and unspent) associated with the ``public_key``.

.. http:get:: /api/v1/outputs?public_key={public_key}

    Return all outputs, both spent and unspent, for the ``public_key``.

   **Example request**:

   .. sourcecode:: http

     GET /api/v1/outputs?public_key=1AAAbbb...ccc HTTP/1.1
     Host: example.com

   **Example response**:

   .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     [
       {
         "output_index": 0,
         "transaction_id": "2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e"
       },
       {
         "output_index": 1,
         "transaction_id": "2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e"
       }
     ]

   :statuscode 200: A list of outputs was found and returned in the body of the response.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``public_key`` querystring was not included in the request.

.. http:get:: /api/v1/outputs?public_key={public_key}&spent=true

    Return all **spent** outputs for ``public_key``.

   **Example request**:

   .. sourcecode:: http

     GET /api/v1/outputs?public_key=1AAAbbb...ccc&spent=true HTTP/1.1
     Host: example.com

   **Example response**:

   .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     [
       {
         "output_index": 0,
         "transaction_id": "2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e"
       }
     ]

   :statuscode 200: A list of outputs were found and returned in the body of the response.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``public_key`` querystring was not included in the request.

.. http:get:: /api/v1/outputs?public_key={public_key}&spent=false

    Return all **unspent** outputs for ``public_key``.

   **Example request**:

   .. sourcecode:: http

     GET /api/v1/outputs?public_key=1AAAbbb...ccc&spent=false HTTP/1.1
     Host: example.com

   **Example response**:

   .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     [
       {
         "output_index": 1,
         "transaction_id": "2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e"
       }
     ]

   :statuscode 200: A list of outputs were found and returned in the body of the response.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``public_key`` querystring was not included in the request.


Assets
------

.. note::

   If you want to do more sophisticated queries
   than those provided by the BigchainDB HTTP API,
   then one option is to connect to MongoDB directly (if possible)
   and do whatever queries MongoDB allows.
   For more about that option, see
   `the page about querying BigchainDB <https://docs.bigchaindb.com/en/latest/query.html>`_.

.. http:get:: /api/v1/assets

   Return all the assets that match a given text search.

   :query string search: Text search string to query.
   :query int limit: (Optional) Limit the number of returned assets. Defaults
                     to ``0`` meaning return all matching assets.

.. http:get:: /api/v1/assets/?search={search}

    Return all assets that match a given text search.

    .. note::

       The ``id`` of the asset
       is the same ``id`` of the CREATE transaction that created the asset.

    .. note::

       You can use ``assets/?search`` or ``assets?search``.

    If no assets match the text search it returns an empty list.

    If the text string is empty or the server does not support text search,
    a ``400 Bad Request`` is returned.

    The results are sorted by text score.
    For more information about the behavior of text search, see `MongoDB text
    search behavior <https://docs.mongodb.com/manual/reference/operator/query/text/#behavior>`_.

   **Example request**:

   .. sourcecode:: http

        GET /api/v1/assets/?search=bigchaindb HTTP/1.1
        Host: example.com

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-type: application/json

        [
            {
                "data": {"msg": "Hello BigchainDB 1!"},
                "id": "51ce82a14ca274d43e4992bbce41f6fdeb755f846e48e710a3bbb3b0cf8e4204"
            },
            {
                "data": {"msg": "Hello BigchainDB 2!"},
                "id": "b4e9005fa494d20e503d916fa87b74fe61c079afccd6e084260674159795ee31"
            },
            {
                "data": {"msg": "Hello BigchainDB 3!"},
                "id": "fa6bcb6a8fdea3dc2a860fcdc0e0c63c9cf5b25da8b02a4db4fb6a2d36d27791"
            }
        ]

   :resheader Content-Type: ``application/json``

   :statuscode 200: The query was executed successfully.
   :statuscode 400: The query was not executed successfully. Returned if the
                    text string is empty or the server does not support
                    text search.

.. http:get:: /api/v1/assets?search={search}&limit={n_documents}

    Return at most ``n_documents`` assets that match a given text search.

    If no assets match the text search it returns an empty list.

    If the text string is empty or the server does not support text search,
    a ``400 Bad Request`` is returned.

    The results are sorted by text score.
    For more information about the behavior of text search, see `MongoDB text
    search behavior <https://docs.mongodb.com/manual/reference/operator/query/text/#behavior>`_.

   **Example request**:

   .. sourcecode:: http

    GET /api/v1/assets?search=bigchaindb&limit=2 HTTP/1.1
    Host: example.com

   **Example response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-type: application/json

    [
        {
            "data": {"msg": "Hello BigchainDB 1!"},
            "id": "51ce82a14ca274d43e4992bbce41f6fdeb755f846e48e710a3bbb3b0cf8e4204"
        },
        {
            "data": {"msg": "Hello BigchainDB 2!"},
            "id": "b4e9005fa494d20e503d916fa87b74fe61c079afccd6e084260674159795ee31"
        },
    ]

   :resheader Content-Type: ``application/json``

   :statuscode 200: The query was executed successfully.
   :statuscode 400: The query was not executed successfully. Returned if the
                    text string is empty or the server does not support
                    text search.


Transaction Metadata
--------------------

.. note::

   If you want to do more sophisticated queries
   than those provided by the BigchainDB HTTP API,
   then one option is to connect to MongoDB directly (if possible)
   and do whatever queries MongoDB allows.
   For more about that option, see
   `the page about querying BigchainDB <https://docs.bigchaindb.com/en/latest/query.html>`_.

.. http:get:: /api/v1/metadata

   Return all the metadata objects that match a given text search.

   :query string search: Text search string to query.
   :query int limit: (Optional) Limit the number of returned metadata objects. Defaults
                     to ``0`` meaning return all matching objects.

.. http:get:: /api/v1/metadata/?search={search}

    Return all metadata objects that match a given text search.

    .. note::

       The ``id`` of the metadata
       is the same ``id`` of the transaction where it was defined.

    .. note::

       You can use ``metadata/?search`` or ``metadata?search``.

    If no metadata objects match the text search it returns an empty list.

    If the text string is empty or the server does not support text search,
    a ``400 Bad Request`` is returned.

    The results are sorted by text score.
    For more information about the behavior of text search, see `MongoDB text
    search behavior <https://docs.mongodb.com/manual/reference/operator/query/text/#behavior>`_.

   **Example request**:

   .. sourcecode:: http

        GET /api/v1/metadata/?search=bigchaindb HTTP/1.1
        Host: example.com

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-type: application/json

        [
            {
                "metadata": {"metakey1": "Hello BigchainDB 1!"},
                "id": "51ce82a14ca274d43e4992bbce41f6fdeb755f846e48e710a3bbb3b0cf8e4204"
            },
            {
                "metadata": {"metakey2": "Hello BigchainDB 2!"},
                "id": "b4e9005fa494d20e503d916fa87b74fe61c079afccd6e084260674159795ee31"
            },
            {
                "metadata": {"metakey3": "Hello BigchainDB 3!"},
                "id": "fa6bcb6a8fdea3dc2a860fcdc0e0c63c9cf5b25da8b02a4db4fb6a2d36d27791"
            }
        ]

   :resheader Content-Type: ``application/json``

   :statuscode 200: The query was executed successfully.
   :statuscode 400: The query was not executed successfully. Returned if the
                    text string is empty or the server does not support
                    text search.

.. http:get:: /api/v1/metadata/?search={search}&limit={n_documents}

    Return at most ``n_documents`` metadata objects that match a given text search.

    If no metadata objects match the text search it returns an empty list.

    If the text string is empty or the server does not support text search,
    a ``400 Bad Request`` is returned.

    The results are sorted by text score.
    For more information about the behavior of text search, see `MongoDB text
    search behavior <https://docs.mongodb.com/manual/reference/operator/query/text/#behavior>`_.

   **Example request**:

   .. sourcecode:: http

    GET /api/v1/metadata?search=bigchaindb&limit=2 HTTP/1.1
    Host: example.com

   **Example response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-type: application/json

    [
        {
            "metadata": {"msg": "Hello BigchainDB 1!"},
            "id": "51ce82a14ca274d43e4992bbce41f6fdeb755f846e48e710a3bbb3b0cf8e4204"
        },
        {
            "metadata": {"msg": "Hello BigchainDB 2!"},
            "id": "b4e9005fa494d20e503d916fa87b74fe61c079afccd6e084260674159795ee31"
        },
    ]

   :resheader Content-Type: ``application/json``

   :statuscode 200: The query was executed successfully.
   :statuscode 400: The query was not executed successfully. Returned if the
                    text string is empty or the server does not support
                    text search.


Validators
--------------------

.. http:get:: /api/v1/validators

    Return the local validators set of a given node.

   **Example request**:

   .. sourcecode:: http

    GET /api/v1/validators HTTP/1.1
    Host: example.com

   **Example response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-type: application/json

    [
        {
            "pub_key": {
                   "data":"4E2685D9016126864733225BE00F005515200727FBAB1312FC78C8B76831255A",
                   "type":"ed25519"
            },
            "power": 10
        },
        {
             "pub_key": {
                   "data":"608D839D7100466D6BA6BE79C320F8B81DE93CFAA58CF9768CF921C6371F2553",
                   "type":"ed25519"
             },
             "power": 5
        }
    ]


   :resheader Content-Type: ``application/json``

   :statuscode 200: The query was executed successfully and validators set was returned.


Blocks
------

.. http:get:: /api/v1/blocks/{block_height}

   Get the block with the height ``block_height``.

   :param block_height: block height
   :type block_height: integer

   **Example request**:

   .. literalinclude:: http-samples/get-block-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-block-response.http
      :language: http


   :resheader Content-Type: ``application/json``

   :statuscode 200: A block with that block height was found.
   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/blocks`` without the ``block_height``.
   :statuscode 404: A block with that block height was not found.


.. http:get:: /api/v1/blocks

   The unfiltered ``/blocks`` endpoint without any query parameters
   returns a ``400 Bad Request`` status code.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/blocks HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request

   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/blocks`` without the ``block_height``.


.. http:get:: /api/v1/blocks?transaction_id={transaction_id}

   Retrieve a list of block IDs (block heights), such that the blocks with those IDs contain a transaction with the ID ``transaction_id``. A correct response may consist of an empty list or a list with one block ID.

   .. note::
       In case no block was found, an empty list and an HTTP status code
       ``200 OK`` is returned, as the request was still successful.

   :query string transaction_id: (Required) transaction ID

   **Example request**:

   .. literalinclude:: http-samples/get-block-txid-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-block-txid-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: The request was properly formed and zero or more blocks were found containing the specified ``transaction_id``.
   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/blocks``, without defining ``transaction_id``.


.. _determining-the-api-root-url:

Determining the API Root URL
----------------------------

When you start BigchainDB Server using ``bigchaindb start``,
an HTTP API is exposed at some address. The default is:

``http://localhost:9984/api/v1/``

It's bound to ``localhost``,
so you can access it from the same machine,
but it won't be directly accessible from the outside world.
(The outside world could connect via a SOCKS proxy or whatnot.)

The documentation about BigchainDB Server :doc:`Configuration Settings <server-reference/configuration>`
has a section about how to set ``server.bind`` so as to make
the HTTP API publicly accessible.

If the API endpoint is publicly accessible,
then the public API Root URL is determined as follows:

- The public IP address (like 12.34.56.78)
  is the public IP address of the machine exposing
  the HTTP API to the public internet (e.g. either the machine hosting
  Gunicorn or the machine running the reverse proxy such as NGINX).
  It's determined by AWS, Azure, Rackspace, or whoever is hosting the machine.

- The DNS hostname (like example.com) is determined by DNS records,
  such as an "A Record" associating example.com with 12.34.56.78

- The port (like 9984) is determined by the ``server.bind`` setting
  if Gunicorn is exposed directly to the public Internet.
  If a reverse proxy (like NGINX) is exposed directly to the public Internet
  instead, then it could expose the HTTP API on whatever port it wants to.
  (It should expose the HTTP API on port 9984, but it's not bound to do
  that by anything other than convention.)
