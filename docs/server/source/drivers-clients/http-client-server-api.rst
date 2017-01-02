The HTTP Client-Server API
==========================

This page assumes you already know an API Root URL
for a BigchainDB node or reverse proxy.
It should be something like ``http://apihosting4u.net:9984``
or ``http://12.34.56.78:9984``.

If you set up a BigchainDB node or reverse proxy yourself,
and you're not sure what the API Root URL is,
then see the last section of this page for help.


BigchainDB Root URL
-------------------

If you send an HTTP GET request to the API Root URL
e.g. ``http://localhost:9984`` 
or ``http://apihosting4u.net:9984``
(with no ``/api/v1/`` on the end), 
then you should get an HTTP response 
with something like the following in the body:

.. code-block:: json

    {
      "_links": {
        "docs": { "href": "https://docs.bigchaindb.com/projects/server/en/v0.9.0/" }
      }
      "keyring": [
        "6qHyZew94NMmUTYyHnkZsB8cxJYuRNEiEpXHe1ih9QX3",
        "AdDuyrTyjrDt935YnFu4VBCVDhHtY2Y6rcy7x2TFeiRi"
      ],
      "public_key": "AiygKSRhZWTxxYT4AfgKoTG4TZAoPsWoEt6C6bLq4jJR",
      "software": "BigchainDB",
      "version": "0.9.0",
    }


API Root Endpoint
-------------------

If you send an HTTP GET request to the API Root Endpoint
e.g. ``http://localhost:9984/api/v0.9/``
or ``http://apihosting4u.net:9984/api/v0.9/``,
then you should get an HTTP response
that allows you to discover the BigchainDB API endpoints:

.. code-block:: json

    {
      "_links": {
        "blocks": { "href": "/blocks" },
        "docs": { "href": "https://docs.bigchaindb.com/projects/server/en/v0.9.0/drivers-clients/http-client-server-api.html" },
        "self": { "href": "/" },
        "statuses": { "href": "/statuses" },
        "transactions": { "href": "/transactions" },
        "votes": { "href": "/votes" }
      },
      "version" : "0.9.0"
    }

Transactions
-------------------

.. http:get:: /transactions/{tx_id}

   Get the transaction with the ID ``tx_id``.

   This endpoint returns only a transaction from a ``VALID`` or ``UNDECIDED``
   block on ``bigchain``, if exists.

   A transaction itself doesn't include a ``timestamp`` property. Only the
   block a transaction was included in has a unix ``timestamp`` property. It is
   returned by this endpoint in a HTTP custom entity header called
   ``X-BigchainDB-Timestamp``.

   :param tx_id: transaction ID
   :type tx_id: hex string

   **Example request**:

   .. literalinclude:: samples/get-tx-id-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-tx-id-response.http
      :language: http

   :resheader X-BigchainDB-Timestamp: A unix timestamp describing when a transaction was included into a valid block. The timestamp provided is taken from the block the transaction was included in.
   :resheader Content-Type: ``application/json``

   :statuscode 200: A transaction with that ID was found.
   :statuscode 404: A transaction with that ID was not found.

.. http:get:: /transactions

   The current ``/transactions`` endpoint returns a ``404 Not Found`` HTTP
   status code. Eventually, this functionality will get implemented.
   We believe a PUSH rather than a PULL pattern is more appropriate, as the
   items returned in the collection would change by the second.

   There are however requests that might come of use, given the endpoint is
   queried correctly. Some of them include retrieving a list of transactions
   that include:

   * `Unfulfilled outputs <#get--transactions?fulfilled=false&public_keys=public_keys>`_
   * `Transactions related to a specific asset <#get--transactions?operation=CREATE|TRANSFER&asset_id=asset_id>`_

   In this section, we've listed those particular requests, as they will likely
   to be very handy when implementing your application on top of BigchainDB.

   .. note::
      Looking up transactions with a specific ``metadata`` field is currently not supported.
      This functionality requires something like custom indexing per client or read-only followers,
      which is not yet on the roadmap.

   A generalization of those parameters follows:

   :query boolean fulfilled: A flag to indicate if transactions with fulfilled conditions should be returned.

   :query string public_keys: Public key able to validly spend an output of a transaction, assuming the user also has the corresponding private key.

   :query string operation: One of the three supported operations of a transaction: ``GENESIS``, ``CREATE``, ``TRANSFER``.

   :query string asset_id: asset ID.

   :statuscode 404: BigchainDB does not expose this endpoint.


.. http:get:: /transactions?fulfilled=false&public_keys={public_keys}

   Get a list of transactions with unfulfilled conditions.

   If the querystring ``fulfilled`` is set to ``false`` and all conditions for
   ``public_keys`` happen to be fulfilled already, this endpoint will return
   an empty list.

   This endpoint returns conditions only if the transaction they're in are
   included in a ``VALID`` or ``UNDECIDED`` block on ``bigchain``.

   :query boolean fulfilled: A flag to indicate if transactions with fulfilled conditions should be returned.

   :query string public_keys: Public key able to validly spend an output of a transaction, assuming the user also has the corresponding private key.

   **Example request**:


   .. literalinclude:: samples/get-tx-unfulfilled-request.http
      :language: http


   **Example response**:

   .. literalinclude:: samples/get-tx-unfulfilled-response.http
      :language: http

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of transactions containing unfulfilled conditions was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``public_keys`` querystring was not included in the request.

.. http:get:: /transactions?operation={GENESIS|CREATE|TRANSFER}&asset_id={asset_id}

   Get a list of transactions that use an asset with the ID ``asset_id``.

   This endpoint returns assets only if the transaction they're in are
   included in a ``VALID`` or ``UNDECIDED`` block on ``bigchain``.

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

   :query string operation: One of the three supported operations of a transaction: ``GENESIS``, ``CREATE``, ``TRANSFER``.

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

   Push a new transaction.

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

   :statuscode 202: The pushed transaction was accepted, but the processing has not been completed.
   :statuscode 400: The transaction was invalid and not created.


Statuses
--------------------------------

.. http:get:: /statuses/{tx_id|block_id}

   Get the status of an asynchronously written resource by their id.

   Supports the retrieval of a status for a transaction using ``tx_id`` or the
   retrieval of a status for a block using ``block_id``.

   The possible status values are ``backlog``, ``undecided``, ``valid`` or
   ``invalid``.

   If a transaction or block is persisted to the chain and it's status is set
   to ``valid`` or ``undecided``, a ``303 See Other`` status code is returned,
   as well as an URL to the resource in the location header.

   :param tx_id: transaction ID
   :type tx_id: hex string

   :param block_id: block ID
   :type block_id: hex string

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

   :statuscode 200: A transaction or block with that ID was found. The status is either ``backlog``, ``invalid``.
   :statuscode 303: A transaction or block with that ID was found and persisted to the chain. A location header to the resource is provided.
   :statuscode 404: A transaction or block with that ID was not found.

Blocks
--------------------------------

.. http:get:: /blocks/{block_id}?status={VALID|UNDECIDED|INVALID}

   Get the block with the ID ``block_id``.

   .. note::
       As ``status``'s default value is set to ``VALID``, only ``VALID`` blocks
       will be returned by this endpoint. In case ``status=VALID``, but a block
       that was labeled ``UNDECIDED`` or ``INVALID`` is requested by
       ``block_id``, this endpoint will return a ``404 Not Found`` status code
       to warn the user. To check a block's status independently, use the
       `Statuses endpoint <#get--statuses-tx_id|block_id>`_.

   :param block_id: block ID
   :type block_id: hex string

   :query string status: Per default set to ``VALID``. One of ``VALID``, ``UNDECIDED`` or ``INVALID``.

   **Example request**:

   .. literalinclude:: samples/get-block-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-block-response.http
      :language: http


   :resheader Content-Type: ``application/json``

   :statuscode 200: A block with that ID was found.
   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/blocks`` without the ``block_id``.
   :statuscode 404: A block with that ID and a certain ``status`` was not found.

.. http:get:: /blocks

   The current ``/blocks`` endpoint returns a ``404 Not Found`` HTTP status
   code. Eventually, this functionality will get implemented.
   We believe a PUSH rather than a PULL pattern is more appropriate, as the
   items returned in the collection would change by the second.

   :statuscode 404: BigchainDB does not expose this endpoint.


.. http:get:: /blocks?tx_id={tx_id}&status={VALID|UNDECIDED|INVALID}

   Retrieve a list of blocks that contain a transaction with the ID ``tx_id``.

   Any blocks, be they ``VALID``, ``UNDECIDED`` or ``INVALID`` will be
   returned. To filter blocks by their status, use the optional ``status``
   querystring.

   .. note::
       In case no block was found, an empty list and an HTTP status code
       ``200 OK`` is returned, as the request was still successful.

   :query string tx_id: transaction ID
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
--------------------------------

.. http:get:: /votes?block_id={block_id}

   Retrieve a list of votes for a certain block with ID ``block_id``.
   To check for the validity of a vote, a user of this endpoint needs to
   perform the `following steps: <https://github.com/bigchaindb/bigchaindb/blob/8ebd93ed3273e983f5770b1617292aadf9f1462b/bigchaindb/util.py#L119>`_

   1. Check if the vote's ``node_pubkey`` is allowed to vote.
   2. Verify the vote's signature against the vote's body (``vote.vote``) and ``node_pubkey``.


   :query string block_id: The block ID to filter the votes.

   **Example request**:

   .. sourcecode:: http

      GET /votes?block_id=6152f...e7202 HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [{
        "node_pubkey": "ErEeVZt8AfLbMJub25tjNxbpzzTNp3mGidL3GxGdd9bt" ,
        "signature": "53wxrEQDYk1dXzmvNSytbCfmNVnPqPkDQaTnAe8Jf43s6ssejPxezkCvUnGTnduNUmaLjhaan1iRLi3peu6s5DzA",
        "vote": {
          "invalid_reason": null ,
          "is_block_valid": true ,
          "previous_block": "6152fbc7e0f7686512ed6b92c01e8c73ea1e3f51a7b037ac5cc8c860215e7202" ,
          "timestamp": "1480082692" ,
          "voting_for_block": "6152f...e7202"
        }
      }]

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of votes voting for a block with ID ``block_id`` was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. just requesting ``/votes``, without defining ``block_id``.


.. http:get:: /votes?block_id={block_id}&voter={voter}

   Description: TODO


Determining the API Root URL
----------------------------

When you start BigchainDB Server using ``bigchaindb start``,
an HTTP API is exposed at some address. The default is:

`http://localhost:9984/api/v0.9/ <http://localhost:9984/api/v0.9/>`_

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

- The DNS hostname (like apihosting4u.net) is determined by DNS records,
  such as an "A Record" associating apihosting4u.net with 12.34.56.78

- The port (like 9984) is determined by the ``server.bind`` setting
  if Gunicorn is exposed directly to the public Internet.
  If a reverse proxy (like Nginx) is exposed directly to the public Internet
  instead, then it could expose the HTTP API on whatever port it wants to.
  (It should expose the HTTP API on port 9984, but it's not bound to do
  that by anything other than convention.)
