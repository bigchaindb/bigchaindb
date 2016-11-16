The HTTP Client-Server API
==========================

.. note::

   The HTTP client-server API is currently quite rudimentary. For example,
   there is no ability to do complex queries using the HTTP API. We plan to add
   more querying capabilities in the future.

This page assumes you already know an API Root URL
for a BigchainDB node or reverse proxy.
It should be something like ``http://apihosting4u.net:9984``
or ``http://12.34.56.78:9984``.

If you set up a BigchainDB node or reverse proxy yourself,
and you're not sure what the API Root URL is,
then see the last section of this page for help.


API Root URL
------------

If you send an HTTP GET request to the API Root URL
e.g. ``http://localhost:9984`` 
or ``http://apihosting4u.net:9984``
(with no ``/api/v1/`` on the end), 
then you should get an HTTP response 
with something like the following in the body:

.. code-block:: json

    {
      "keyring": [
        "6qHyZew94NMmUTYyHnkZsB8cxJYuRNEiEpXHe1ih9QX3",
        "AdDuyrTyjrDt935YnFu4VBCVDhHtY2Y6rcy7x2TFeiRi"
      ],
      "public_key": "AiygKSRhZWTxxYT4AfgKoTG4TZAoPsWoEt6C6bLq4jJR",
      "software": "BigchainDB",
      "version": "0.6.0"
    }


POST /transactions/
-------------------

.. http:post:: /transactions/

   Push a new transaction.

   Note: The posted transaction should be a valid and signed :doc:`transaction <../data-models/transaction-model>`.
   The steps to build a valid transaction are beyond the scope of this page.
   One would normally use a driver such as the `BigchainDB Python Driver
   <https://docs.bigchaindb.com/projects/py-driver/en/latest/index.html>`_ to
   build a valid transaction. The exact contents of a valid transaction depend 
   on the associated public/private keypairs.

   **Example request**:

   .. literalinclude:: samples/post-tx-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/post-tx-response.http
      :language: http

   :statuscode 202: The pushed transaction was accepted, but the processing has not been completed.
   :statuscode 400: The transaction was invalid and not created.


GET /transactions/{tx_id}/status
--------------------------------

.. http:get:: /transactions/{tx_id}/status

   Get the status of the transaction with the ID ``tx_id``, if a transaction
   with that ``tx_id`` exists.

   The possible status values are ``backlog``, ``undecided``, ``valid`` or
   ``invalid``.

   :param tx_id: transaction ID
   :type tx_id: hex string

   **Example request**:

   .. literalinclude:: samples/get-tx-status-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-tx-status-response.http
      :language: http

   :statuscode 200: A transaction with that ID was found and the status is returned.
   :statuscode 404: A transaction with that ID was not found.


GET /transactions/{tx_id}
-------------------------

.. http:get:: /transactions/{tx_id}

   Get the transaction with the ID ``tx_id``.

   This endpoint returns only a transaction from a ``VALID`` or ``UNDECIDED``
   block on ``bigchain``, if exists.

   :param tx_id: transaction ID
   :type tx_id: hex string

   **Example request**:

   .. literalinclude:: samples/get-tx-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-tx-response.http
      :language: http

   :statuscode 200: A transaction with that ID was found.
   :statuscode 404: A transaction with that ID was not found.


GET /transactions/{tx_id}/conditions/{cid}
-------------------------

.. http:get:: /transactions/{tx_id}/conditions/{cid}

   Returns the condition with index ``cid`` from a transaction with ID
   ``txid``.

   If either a transaction with ID ``txid`` isn't found or the condition
   requested at the index ``cid`` is not found, this endpoint will return a
   ``400 Bad Request``.

   :param tx_id: transaction ID
   :type tx_id: hex string

   :param cid: A condition's index in the transaction
   :type cid: integer

   **Example request**:

   .. sourcecode:: http

      GET /transactions/2d431...0b4b0e/conditions/0 HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "condition": {
          "uri": "cc:4:20:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkk:96",
          "details": {
            "signature": null,
            "type": "fulfillment",
            "type_id": 4,
            "bitmask": 32,
            "public_key": "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
          }
        }
      }

   :statuscode 200: A condition with ``cid`` was found in a transaction with ID ``tx_id``.
   :statuscode 400: Either a transaction with ``tx_id`` or a condition with ``cid`` wasn't found.


GET /unspents/
-------------------------

.. note::

   This endpoint (unspents) is not yet implemented. We published it here for preview and comment.
   

.. http:get:: /unspents?owner_after={owner_after}

   Get a list of links to transactions' outputs that have not been used in
   a previous transaction and could hence be called unspent outputs
   (or simply: unspents).

   This endpoint will return a ``HTTP 400 Bad Request`` if the querystring
   ``owner_after`` happens to not be defined in the request.

   Note that if unspents for a certain ``public_key`` have not been found by
   the server, this will result in the server returning a 200 OK HTTP status
   code and an empty list in the response's body.

   :param owner_after: A public key, able to validly spend an output of a transaction, assuming the user also has the corresponding private key.
   :type owner_after: base58 encoded string

   **Example request**:

   .. sourcecode:: http

      GET /unspents?owner_after=1AAAbbb...ccc HTTP/1.1
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
   :statuscode 400: The request wasn't understood by the server, e.g. the ``owner_after`` querystring was not included in the request.


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

- The DNS hostname (like apihosting4u.net) is determined by DNS records, 
  such as an "A Record" associating apihosting4u.net with 12.34.56.78

- The port (like 9984) is determined by the ``server.bind`` setting 
  if Gunicorn is exposed directly to the public Internet. 
  If a reverse proxy (like Nginx) is exposed directly to the public Internet 
  instead, then it could expose the HTTP API on whatever port it wants to. 
  (It should expose the HTTP API on port 9984, but it's not bound to do 
  that by anything other than convention.)
