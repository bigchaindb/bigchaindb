The HTTP Client-Server API
==========================

This page assumes you already know an API Root URL
for a BigchainDB node or reverse proxy.
It should be something like ``https://example.com:9984``
or ``https://12.34.56.78:9984``.

If you set up a BigchainDB node or reverse proxy yourself,
and you're not sure what the API Root URL is,
then see the last section of this page for help.


BigchainDB Root URL
-------------------

If you send an HTTP GET request to the BigchainDB Root URL
e.g. ``http://localhost:9984``
or ``https://example.com:9984``
(with no ``/api/v1/`` on the end),
then you should get an HTTP response
with something like the following in the body:

.. code-block:: json

    {
      "_links": {
        "docs": "https://docs.bigchaindb.com/projects/server/en/v0.9.0/",
        "api_v1": "http://example.com:9984/api/v1/"
      },
      "keyring": [
        "6qHyZew94NMmUTYyHnkZsB8cxJYuRNEiEpXHe1ih9QX3",
        "AdDuyrTyjrDt935YnFu4VBCVDhHtY2Y6rcy7x2TFeiRi"
      ],
      "public_key": "AiygKSRhZWTxxYT4AfgKoTG4TZAoPsWoEt6C6bLq4jJR",
      "software": "BigchainDB",
      "version": "0.9.0"
    }


API Root Endpoint
-------------------

If you send an HTTP GET request to the API Root Endpoint
e.g. ``http://localhost:9984/api/v1/``
or ``https://example.com:9984/api/v1/``,
then you should get an HTTP response
that allows you to discover the BigchainDB API endpoints:

.. code-block:: json

    {
      "_links": {
        "docs": "https://docs.bigchaindb.com/projects/server/en/v0.9.0/drivers-clients/http-client-server-api.html",
        "self": "https://example.com:9984/api/v1",
        "statuses": "https://example.com:9984/api/v1/statuses",
        "transactions": "https://example.com:9984/api/v1/transactions",
      },
      "version" : "0.9.0"
    }

Transactions
-------------------

.. http:get:: /transactions/{tx_id}

   Get the transaction with the ID ``tx_id``.

   This endpoint returns only a transaction from the ``BACKLOG`` or a ``VALID`` or ``UNDECIDED``
   block on ``bigchain``, if exists.

   :param tx_id: transaction ID
   :type tx_id: hex string

   **Example request**:

   .. literalinclude:: samples/get-tx-id-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-tx-id-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A transaction with that ID was found.
   :statuscode 404: A transaction with that ID was not found.

.. http:get:: /transactions

   The unfiltered ``/transactions`` endpoint without any query parameters
   returns a status code `400`. For valid filters, see the sections below.

   **Example request**:

   .. sourcecode:: http

      GET /transactions HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request

   :statuscode 400: The request wasn't understood by the server, a mandatory querystring was not included in the request.

   There are however filtered requests that might come of use, given the endpoint is
   queried correctly. Some of them include retrieving a list of transactions
   that include:

   * `Unspent outputs <#get--transactions?unspent=true&public_keys=public_keys>`_
   * `Transactions related to a specific asset <#get--transactions?operation=CREATE|TRANSFER&asset_id=asset_id>`_

   In this section, we've listed those particular requests, as they will likely
   to be very handy when implementing your application on top of BigchainDB.

   .. note::
      Looking up transactions with a specific ``metadata`` field is currently not supported.
      This functionality requires something like custom indexing per client or read-only followers,
      which is not yet on the roadmap.

   A generalization of those parameters follows:

   :query boolean unspent: A flag to indicate whether only transactions with unspent outputs should be returned.

   :query string public_keys: Public key able to validly spend an output of a transaction, assuming the user also has the corresponding private key.

   :query string operation: One of the two supported operations of a transaction: ``CREATE``, ``TRANSFER``.

   :query string asset_id: asset ID.


.. http:get:: /transactions?unspent=true&public_keys={public_keys}

   Get a list of transactions with unspent outputs.

   If the querystring ``unspent`` is set to ``false`` and all outputs for
   ``public_keys`` happen to be spent already, this endpoint will return
   an empty list. Transactions with multiple outputs that have not all been spent
   will be included in the response.

   This endpoint returns transactions only if they are
   included in the ``BACKLOG`` or in a ``VALID`` or ``UNDECIDED`` block on ``bigchain``.

   :query boolean unspent: A flag to indicate if transactions with unspent outputs should be returned.

   :query string public_keys: Public key able to validly spend an output of a transaction, assuming the user also has the corresponding private key.

   **Example request**:


   .. literalinclude:: samples/get-tx-unspent-request.http
      :language: http


   **Example response**:

   .. literalinclude:: samples/get-tx-unspent-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of transactions containing unspent outputs was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``public_keys`` querystring was not included in the request.

.. http:get:: /transactions?operation={CREATE|TRANSFER}&asset_id={asset_id}

   Get a list of transactions that use an asset with the ID ``asset_id``.
   Every ``TRANSFER`` transaction that originates from a ``CREATE`` transaction
   with ``asset_id`` will be included. This allows users to query the entire history or
   provenance of an asset.

   This endpoint returns transactions only if they are
   included in the ``BACKLOG`` or in a ``VALID`` or ``UNDECIDED`` block on ``bigchain``.

   .. note::
       The BigchainDB API currently doesn't expose an
       ``/assets/{asset_id}`` endpoint, as there wouldn't be any way for a
       client to verify that what was received is consistent with what was
       persisted in the database.
       However, BigchainDB's consensus ensures that any ``asset_id`` is
       a unique key identifying an asset, meaning that when calling
       ``/transactions?operation=CREATE&asset_id={asset_id}``, there will in
       any case only be one transaction returned (in a list though, since
       ``/transactions`` is a list-returning endpoint).
       Leaving out the ``asset_id`` query and calling
       ``/transactions?operation=CREATE`` returns the list of assets.

   :query string operation: One of the two supported operations of a transaction: ``CREATE``, ``TRANSFER``.

   :query string asset_id: asset ID.

   **Example request**:

   .. literalinclude:: samples/get-tx-by-asset-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-tx-by-asset-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of transactions containing an asset with ID ``asset_id`` was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``asset_id`` querystring was not included in the request.


.. http:post:: /transactions

   Push a new transaction. The endpoint will return a ``statuses`` endpoint to track
   the status of the transaction.

   .. note::
       The posted transaction should be valid `transaction
       <https://bigchaindb.readthedocs.io/en/latest/data-models/transaction-model.html>`_.
       The steps to build a valid transaction are beyond the scope of this page.
       One would normally use a driver such as the `BigchainDB Python Driver
       <https://docs.bigchaindb.com/projects/py-driver/en/latest/index.html>`_
       to build a valid transaction.

   **Example request**:

   .. literalinclude:: samples/post-tx-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/post-tx-response.http
      :language: http

   :resheader Content-Type: ``application/json``
   :resheader Location: As the transaction will be persisted asynchronously, an endpoint to monitor its status is provided in this header.

   :statuscode 202: The pushed transaction was accepted in the ``BACKLOG``, but the processing has not been completed.
   :statuscode 400: The transaction was malformed and not accepted in the ``BACKLOG``.


Statuses
--------------------------------

.. http:get:: /statuses

   Get the status of an asynchronously written transaction or block by their id.

   The possible status values are ``undecided``, ``valid`` or ``invalid`` for
   both blocks and transactions. An additional state ``backlog`` is provided
   for transactions.

   A link to the resource is also provided in the returned payload under
   ``_links``.

   :query string tx_id: transaction ID
   :query string block_id: block ID

   .. note::

        Exactly one of the ``tx_id`` or ``block_id`` query parameters must be
        used together with this endpoint (see below for getting `transaction
        statuses <#get--statuses?tx_id=tx_id>`_ and `block statuses
        <#get--statuses?block_id=block_id>`_).


.. http:get:: /statuses?tx_id={tx_id}

    Get the status of a transaction.

   **Example request**:

   .. literalinclude:: samples/get-statuses-tx-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-statuses-tx-invalid-response.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-statuses-tx-valid-response.http
      :language: http

   :resheader Content-Type: ``application/json``
   :resheader Location: Once the transaction has been persisted, this header will link to the actual resource.

   :statuscode 200: A transaction with that ID was found.
   :statuscode 404: A transaction with that ID was not found.


.. http:get:: /statuses?block_id={block_id}

    Get the status of a block.

   **Example request**:

   .. literalinclude:: samples/get-statuses-block-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-statuses-block-invalid-response.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-statuses-block-valid-response.http
      :language: http

   :resheader Content-Type: ``application/json``
   :resheader Location: Once the block has been persisted, this header will link to the actual resource.

   :statuscode 200: A block with that ID was found.
   :statuscode 404: A block with that ID was not found.


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

.. http:get:: /blocks/{block_id}

   Get the block with the ID ``block_id``. Any blocks, be they ``VALID``, ``UNDECIDED`` or ``INVALID`` will be
   returned. To check a block's status independently, use the `Statuses endpoint <#status>`_.
   To check the votes on a block, have a look at the `votes endpoint <#votes>`_.

   :param block_id: block ID
   :type block_id: hex string

   **Example request**:

   .. literalinclude:: samples/get-block-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-block-response.http
      :language: http


   :resheader Content-Type: ``application/json``

   :statuscode 200: A block with that ID was found.
   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/blocks`` without the ``block_id``.
   :statuscode 404: A block with that ID was not found.


.. http:get:: /blocks

   The unfiltered ``/blocks`` endpoint without any query parameters returns a `400` status code.
   The list endpoint should be filtered with a ``tx_id`` query parameter,
   see the ``/blocks?tx_id={tx_id}&status={UNDECIDED|VALID|INVALID}``
   `endpoint <#get--blocks?tx_id=tx_id&status=UNDECIDED|VALID|INVALID>`_.


   **Example request**:

   .. sourcecode:: http

      GET /blocks HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request

   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/blocks`` without the ``block_id``.

.. http:get:: /blocks?tx_id={tx_id}&status={UNDECIDED|VALID|INVALID}

   Retrieve a list of ``block_id`` with their corresponding status that contain a transaction with the ID ``tx_id``.

   Any blocks, be they ``UNDECIDED``, ``VALID`` or ``INVALID`` will be
   returned if no status filter is provided.

   .. note::
       In case no block was found, an empty list and an HTTP status code
       ``200 OK`` is returned, as the request was still successful.

   :query string tx_id: transaction ID *(required)*
   :query string status: Filter blocks by their status. One of ``VALID``, ``UNDECIDED`` or ``INVALID``.

   **Example request**:

   .. literalinclude:: samples/get-block-txid-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-block-txid-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of blocks containing a transaction with ID ``tx_id`` was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/blocks``, without defining ``tx_id``.




Votes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /votes?block_id={block_id}

   Retrieve a list of votes for a certain block with ID ``block_id``.
   To check for the validity of a vote, a user of this endpoint needs to
   perform the `following steps: <https://github.com/bigchaindb/bigchaindb/blob/8ebd93ed3273e983f5770b1617292aadf9f1462b/bigchaindb/util.py#L119>`_

   1. Check if the vote's ``node_pubkey`` is allowed to vote.
   2. Verify the vote's signature against the vote's body (``vote.vote``) and ``node_pubkey``.


   :query string block_id: The block ID to filter the votes.

   **Example request**:

   .. literalinclude:: samples/get-vote-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-vote-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of votes voting for a block with ID ``block_id`` was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/votes``, without defining ``block_id``.


Determining the API Root URL
----------------------------

When you start BigchainDB Server using ``bigchaindb start``,
an HTTP API is exposed at some address. The default is:

`http://localhost:9984/api/v1/ <http://localhost:9984/api/v1/>`_

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
