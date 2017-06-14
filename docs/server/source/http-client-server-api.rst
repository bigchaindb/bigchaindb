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


API Root Endpoint
-------------------

If you send an HTTP GET request to the API Root Endpoint
e.g. ``http://localhost:9984/api/v1/``
or ``https://example.com:9984/api/v1/``,
then you should get an HTTP response
that allows you to discover the BigchainDB API endpoints:

.. literalinclude:: http-samples/api-index-response.http
    :language: http


Transactions
-------------------

.. http:get:: /api/v1/transactions/{tx_id}

   Get the transaction with the ID ``tx_id``.

   This endpoint returns a transaction if it was included in a ``VALID`` block.
   All instances of a transaction in invalid/undecided blocks or the backlog
   are ignored and treated as if they don't exist. If a request is made for a
   transaction and instances of that transaction are found only in
   invalid/undecided blocks or the backlog, then the response will be ``404 Not
   Found``.

   :param tx_id: transaction ID
   :type tx_id: hex string

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

   The unfiltered ``/api/v1/transactions`` endpoint without any query parameters
   returns a status code `400`. For valid filters, see the sections below.

   There are however filtered requests that might come of use, given the endpoint is
   queried correctly. Some of them include retrieving a list of transactions
   that include:

   * `Transactions related to a specific asset <#get--transactions?asset_id=asset_id&operation=CREATE|TRANSFER>`_

   In this section, we've listed those particular requests, as they will likely
   to be very handy when implementing your application on top of BigchainDB.

   .. note::
      Looking up transactions with a specific ``metadata`` field is currently not supported,
      however, providing a way to query based on ``metadata`` data is on our roadmap.

   A generalization of those parameters follows:

   :query string asset_id: The ID of the asset.

   :query string operation: (Optional) One of the two supported operations of a transaction: ``CREATE``, ``TRANSFER``.

.. http:get:: /api/v1/transactions?asset_id={asset_id}&operation={CREATE|TRANSFER}

   Get a list of transactions that use an asset with the ID ``asset_id``.
   Every ``TRANSFER`` transaction that originates from a ``CREATE`` transaction
   with ``asset_id`` will be included. This allows users to query the entire history or
   provenance of an asset.

   This endpoint returns transactions only if they are decided ``VALID`` by the server.

   :query string operation: (Optional) One of the two supported operations of a transaction: ``CREATE``, ``TRANSFER``.

   :query string asset_id: asset ID.

   **Example request**:

   .. literalinclude:: http-samples/get-tx-by-asset-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-tx-by-asset-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of transactions containing an asset with ID ``asset_id`` was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``asset_id`` querystring was not included in the request.


.. http:post:: /api/v1/transactions

   Push a new transaction.

   .. note::
       The posted `transaction
       <https://docs.bigchaindb.com/projects/server/en/latest/data-models/transaction-model.html>`_
       should be structurally valid and not spending an already spent output.
       The steps to build a valid transaction are beyond the scope of this page.
       One would normally use a driver such as the `BigchainDB Python Driver
       <https://docs.bigchaindb.com/projects/py-driver/en/latest/index.html>`_
       to build a valid transaction.

   **Example request**:

   .. literalinclude:: http-samples/post-tx-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/post-tx-response.http
      :language: http

   .. note::
       If the server is returning a ``202`` HTTP status code, then the
       transaction has been accepted for processing. To check the status of the
       transaction, poll the link to the `status monitor
       <https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html#get--api-v1-statuses?tx_id=tx_id>`_
       provided in the ``Location`` header or listen to server's
       :ref:`WebSocket Event Stream API <The WebSocket Event Stream API>`.

   :resheader Content-Type: ``application/json``
   :resheader Location: Relative link to a status monitor for the submitted transaction.

   :statuscode 202: The pushed transaction was accepted in the ``BACKLOG``, but the processing has not been completed.
   :statuscode 400: The transaction was malformed and not accepted in the ``BACKLOG``.


Transaction Outputs
-------------------

The ``/api/v1/outputs`` endpoint returns transactions outputs filtered by a
given public key, and optionally filtered to only include outputs that have
not already been spent.


.. http:get:: /api/v1/outputs?public_key={public_key}

   Get transaction outputs by public key. The `public_key` parameter must be
   a base58 encoded ed25519 public key associated with transaction output
   ownership.

   Returns a list of links to transaction outputs.

   :param public_key: Base58 encoded public key associated with output ownership. This parameter is mandatory and without it the endpoint will return a ``400`` response code.
   :param unspent: Boolean value ("true" or "false") indicating if the result set should be limited to outputs that are available to spend. Defaults to "false".


   **Example request**:

   .. sourcecode:: http

     GET /api/v1/outputs?public_key=1AAAbbb...ccc HTTP/1.1
     Host: example.com

   **Example response**:

   .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     [
       "../transactions/2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e/outputs/0",
       "../transactions/2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e/outputs/1"
     ]

   :statuscode 200: A list of outputs were found and returned in the body of the response.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``public_key`` querystring was not included in the request.


Statuses
--------------------------------

.. http:get:: /api/v1/statuses

   Get the status of an asynchronously written transaction or block by their id.

   A link to the resource is also provided in the returned payload under
   ``_links``.

   :query string tx_id: transaction ID
   :query string block_id: block ID

   .. note::

        Exactly one of the ``tx_id`` or ``block_id`` query parameters must be
        used together with this endpoint (see below for getting `transaction
        statuses <#get--statuses?tx_id=tx_id>`_ and `block statuses
        <#get--statuses?block_id=block_id>`_).


.. http:get:: /api/v1/statuses?tx_id={tx_id}

    Get the status of a transaction.

    The possible status values are ``undecided``, ``valid`` or ``backlog``.
    If a transaction in neither of those states is found, a ``404 Not Found``
    HTTP status code is returned. `We're currently looking into ways to unambigously let the user know about a transaction's status that was included in an invalid block. <https://github.com/bigchaindb/bigchaindb/issues/1039>`_

   **Example request**:

   .. literalinclude:: http-samples/get-statuses-tx-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-statuses-tx-valid-response.http
      :language: http

   :resheader Content-Type: ``application/json``
   :resheader Location: Once the transaction has been persisted, this header will link to the actual resource.

   :statuscode 200: A transaction with that ID was found.
   :statuscode 404: A transaction with that ID was not found.


.. http:get:: /api/v1/statuses?block_id={block_id}

    Get the status of a block.

    The possible status values are ``undecided``, ``valid`` or ``invalid``.

   **Example request**:

   .. literalinclude:: http-samples/get-statuses-block-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-statuses-block-invalid-response.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-statuses-block-valid-response.http
      :language: http

   :resheader Content-Type: ``application/json``
   :resheader Location: Once the block has been persisted, this header will link to the actual resource.

   :statuscode 200: A block with that ID was found.
   :statuscode 404: A block with that ID was not found.


Assets
--------------------------------

.. http:get:: /api/v1/assets

   Return all the assets that match a given text search.

   :query string text search: Text search string to query.
   :query int limit: (Optional) Limit the number of returned assets. Defaults
                     to ``0`` meaning return all matching assets.

   .. note::

        Currently this enpoint is only supported if the server is running
        MongoDB as the backend.

.. http:get:: /api/v1/assets?search={text_search}

    Return all assets that match a given text search. The asset is returned
    with the ``id`` of the transaction that created the asset.

    If no assets match the text search it returns an empty list.

    If the text string is empty or the server does not support text search,
    a ``400`` is returned.

    The results are sorted by text score.
    For more information about the behavior of text search see `MongoDB text
    search behavior <https://docs.mongodb.com/manual/reference/operator/query/text/#behavior>`_

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

.. http:get:: /api/v1/assets?search={text_search}&limit={n_documents}

    Return at most ``n`` assets that match a given text search.

    If no assets match the text search it returns an empty list.

    If the text string is empty or the server does not support text search,
    a ``400`` is returned.

    The results are sorted by text score.
    For more information about the behavior of text search see `MongoDB text
    search behavior <https://docs.mongodb.com/manual/reference/operator/query/text/#behavior>`_

   **Example request**:

   .. sourcecode:: http

    GET /api/v1/assets/?search=bigchaindb&limit=2 HTTP/1.1
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


Advanced Usage
--------------------------------

The following endpoints are more advanced and meant for debugging and transparency purposes.

More precisely, the `blocks endpoint <#blocks>`_ allows you to retrieve a block by ``block_id`` as well the list of blocks that
a certain transaction with ``tx_id`` occured in (a transaction can occur in multiple ``invalid`` blocks until it
either gets rejected or validated by the system). This endpoint gives the ability to drill down on the lifecycle of a
transaction

The `votes endpoint <#votes>`_ contains all the voting information for a specific block. So after retrieving the
``block_id`` for a given ``tx_id``, one can now simply inspect the votes that happened at a specific time on that block.


Blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1/blocks/{block_id}

   Get the block with the ID ``block_id``. Any blocks, be they ``VALID``, ``UNDECIDED`` or ``INVALID`` will be
   returned. To check a block's status independently, use the `Statuses endpoint <#status>`_.
   To check the votes on a block, have a look at the `votes endpoint <#votes>`_.

   :param block_id: block ID
   :type block_id: hex string

   **Example request**:

   .. literalinclude:: http-samples/get-block-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-block-response.http
      :language: http


   :resheader Content-Type: ``application/json``

   :statuscode 200: A block with that ID was found.
   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/blocks`` without the ``block_id``.
   :statuscode 404: A block with that ID was not found.


.. http:get:: /api/v1/blocks

   The unfiltered ``/blocks`` endpoint without any query parameters returns a `400` status code.
   The list endpoint should be filtered with a ``tx_id`` query parameter,
   see the ``/blocks?tx_id={tx_id}&status={UNDECIDED|VALID|INVALID}``
   `endpoint <#get--blocks?tx_id=tx_id&status=UNDECIDED|VALID|INVALID>`_.


   **Example request**:

   .. sourcecode:: http

      GET /api/v1/blocks HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request

   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/blocks`` without the ``block_id``.

.. http:get:: /api/v1/blocks?tx_id={tx_id}&status={UNDECIDED|VALID|INVALID}

   Retrieve a list of ``block_id`` with their corresponding status that contain a transaction with the ID ``tx_id``.

   Any blocks, be they ``UNDECIDED``, ``VALID`` or ``INVALID`` will be
   returned if no status filter is provided.

   .. note::
       In case no block was found, an empty list and an HTTP status code
       ``200 OK`` is returned, as the request was still successful.

   :query string tx_id: transaction ID *(required)*
   :query string status: Filter blocks by their status. One of ``VALID``, ``UNDECIDED`` or ``INVALID``.

   **Example request**:

   .. literalinclude:: http-samples/get-block-txid-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-block-txid-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of blocks containing a transaction with ID ``tx_id`` was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/blocks``, without defining ``tx_id``.


Votes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1/votes?block_id={block_id}

   Retrieve a list of votes for a certain block with ID ``block_id``.
   To check for the validity of a vote, a user of this endpoint needs to
   perform the `following steps: <https://github.com/bigchaindb/bigchaindb/blob/8ebd93ed3273e983f5770b1617292aadf9f1462b/bigchaindb/util.py#L119>`_

   1. Check if the vote's ``node_pubkey`` is allowed to vote.
   2. Verify the vote's signature against the vote's body (``vote.vote``) and ``node_pubkey``.


   :query string block_id: The block ID to filter the votes.

   **Example request**:

   .. literalinclude:: http-samples/get-vote-request.http
      :language: http

   **Example response**:

   .. literalinclude:: http-samples/get-vote-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of votes voting for a block with ID ``block_id`` was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/votes``, without defining ``block_id``.


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

The documentation about BigchainDB Server :any:`Configuration Settings`
has a section about how to set ``server.bind`` so as to make
the HTTP API publicly accessible.

If the API endpoint is publicly accessible,
then the public API Root URL is determined as follows:

- The public IP address (like 12.34.56.78)
  is the public IP address of the machine exposing
  the HTTP API to the public internet (e.g. either the machine hosting
  Gunicorn or the machine running the reverse proxy such as Nginx).
  It's determined by AWS, Azure, Rackspace, or whoever is hosting the machine.

- The DNS hostname (like example.com) is determined by DNS records,
  such as an "A Record" associating example.com with 12.34.56.78

- The port (like 9984) is determined by the ``server.bind`` setting
  if Gunicorn is exposed directly to the public Internet.
  If a reverse proxy (like Nginx) is exposed directly to the public Internet
  instead, then it could expose the HTTP API on whatever port it wants to.
  (It should expose the HTTP API on port 9984, but it's not bound to do
  that by anything other than convention.)
