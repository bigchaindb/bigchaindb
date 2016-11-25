The HTTP Client-Server API
==========================

.. note::

   The HTTP client-server API is currently quite rudimentary. For example,
   there is no ability to do complex queries using the HTTP API. We plan to add
   more querying capabilities in the future.

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

   .. sourcecode:: http

      GET /transactions/2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json
      X-BigchainDB-Timestamp: 1234567890

      {
        "transaction": {
          "conditions": [
            {
              "cid": 0,
              "condition": {
                "uri": "cc:4:20:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkk:96",
                "details": {
                  "signature": null,
                  "type": "fulfillment",
                  "type_id": 4,
                  "bitmask": 32,
                  "public_key": "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
                }
              },
              "amount": 1,
              "owners_after": [
                "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
              ]
            }
          ],
          "operation": "CREATE",
          "asset": {
            "divisible": false,
            "updatable": false,
            "data": null,
            "id": "aebeab22-e672-4d3b-a187-bde5fda6533d",
            "refillable": false
          },
          "metadata": null,
          "timestamp": "1477578978",
          "fulfillments": [
            {
              "fid": 0,
              "input": null,
              "fulfillment": "cf:4:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkn2VnQaEWvecO1x82Qr2Va_JjFywLKIOEV1Ob9Ofkeln2K89ny2mB-s7RLNvYAVzWNiQnp18_nQEUsvwACEXTYJ",
              "owners_before": [
                "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
              ]
            }
          ]
        },
        "id": "2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e",
        "version": 1
      }

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

   * `Unfulfilled conditions <#get--transactions?fulfilled=false&owners_after=owners_after>`_
   * `A specific asset <#get--transactions?operation=CREATE|TRANSFER&asset_id=asset_id>`_
   * `Specific metadata <#get--transactions?&metadata_id=metadata_id>`_

   In this section, we've listed those particular requests, as they will likely
   to be very handy when implementing your application on top of BigchainDB.
   A generalization of those parameters can follows:

   :query boolean fulfilled: A flag to indicate if transaction's with fulfilled conditions should be returned.

   :query string owners_after: Public key able to validly spend an output of a transaction, assuming the user also has the corresponding private key.

   :query string operation: One of the three supported operations of a transaction: ``GENESIS``, ``CREATE``, ``TRANSFER``.

   :query string asset_id: asset ID.

   :query string metadata_id: metadata ID.

   :statuscode 404: BigchainDB does not expose this endpoint.


.. http:get:: /transactions?fulfilled=false&owners_after={owners_after}

   Get a list of transactions with unfulfilled conditions.

   If the querystring ``fulfilled`` is set to ``false`` and all conditions for
   ``owners_after`` happen to be fulfilled already, this endpoint will return
   an empty list.

   This endpoint returns conditions only if the transaction they're in are
   included in a ``VALID`` or ``UNDECIDED`` block on ``bigchain``.

   :query boolean fulfilled: A flag to indicate if transaction's with fulfilled conditions should be returned.

   :query string owners_after: Public key able to validly spend an output of a transaction, assuming the user also has the corresponding private key.

   **Example request**:

   .. sourcecode:: http

      GET /transactions?fulfilled=false&owners_after=1AAAbbb...ccc HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [{
        "transaction": {
          "conditions": [
            {
              "cid": 0,
              "condition": {
                "uri": "cc:4:20:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkk:96",
                "details": {
                  "signature": null,
                  "type": "fulfillment",
                  "type_id": 4,
                  "bitmask": 32,
                  "public_key": "1AAAbbb...ccc"
                }
              },
              "amount": 1,
              "owners_after": [
                "1AAAbbb...ccc"
              ]
            }
          ],
          "operation": "CREATE",
          "asset": {
            "divisible": false,
            "updatable": false,
            "data": null,
            "id": "aebeab22-e672-4d3b-a187-bde5fda6533d",
            "refillable": false
          },
          "metadata": null,
          "timestamp": "1477578978",
          "fulfillments": [
            {
              "fid": 0,
              "input": null,
              "fulfillment": "cf:4:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkn2VnQaEWvecO1x82Qr2Va_JjFywLKIOEV1Ob9Ofkeln2K89ny2mB-s7RLNvYAVzWNiQnp18_nQEUsvwACEXTYJ",
              "owners_before": [
                "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
              ]
            }
          ]
        },
        "id": "2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e",
        "version": 1
      }]

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of transaction's containing unfulfilled conditions was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``owners_after`` querystring was not included in the request.

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

   .. sourcecode:: http

      GET /transactions?operation=CREATE&asset_id=1AAAbbb...ccc HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [{
        "transaction": {
          "conditions": [
            {
              "cid": 0,
              "condition": {
                "uri": "cc:4:20:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkk:96",
                "details": {
                  "signature": null,
                  "type": "fulfillment",
                  "type_id": 4,
                  "bitmask": 32,
                  "public_key": "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
                }
              },
              "amount": 1,
              "owners_after": [
                "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
              ]
            }
          ],
          "operation": "CREATE",
          "asset": {
            "divisible": false,
            "updatable": false,
            "data": null,
            "id": "1AAAbbb...ccc",
            "refillable": false
          },
          "metadata": null,
          "timestamp": "1477578978",
          "fulfillments": [
            {
              "fid": 0,
              "input": null,
              "fulfillment": "cf:4:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkn2VnQaEWvecO1x82Qr2Va_JjFywLKIOEV1Ob9Ofkeln2K89ny2mB-s7RLNvYAVzWNiQnp18_nQEUsvwACEXTYJ",
              "owners_before": [
                "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
              ]
            }
          ]
        },
        "id": "2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e",
        "version": 1
      }]

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of transaction's containing an asset with ID ``asset_id`` was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``asset_id`` querystring was not included in the request.

.. http:get:: /transactions?metadata_id={metadata_id}

   Get a list of transactions that use metadata with the ID ``metadata_id``.

   This endpoint returns assets only if the transaction they're in are
   included in a ``VALID`` or ``UNDECIDED`` block on ``bigchain``.

   .. note::
       The BigchainDB API currently doesn't expose an
       ``/metadata/{metadata_id}`` endpoint, as there wouldn't be any way for a
       client to verify that what was received is consistent with what was
       persisted in the database.
       However, BigchainDB's consensus ensures that any ``metadata_id`` is
       a unique key identifying metadata, meaning that when calling
       ``/transactions?metadata_id={metadata_id}``, there will in any case only
       be one transaction returned (in a list though, since ``/transactions``
       is a list-returning endpoint).

   :query string metadata_id: metadata ID.

   **Example request**:

   .. sourcecode:: http

      GET /transactions?metadata_id=1AAAbbb...ccc HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [{
        "transaction": {
          "conditions": [
            {
              "cid": 0,
              "condition": {
                "uri": "cc:4:20:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkk:96",
                "details": {
                  "signature": null,
                  "type": "fulfillment",
                  "type_id": 4,
                  "bitmask": 32,
                  "public_key": "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
                }
              },
              "amount": 1,
              "owners_after": [
                "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
              ]
            }
          ],
          "operation": "CREATE",
          "asset": {
            "divisible": false,
            "updatable": false,
            "data": null,
            "id": "aebeab22-e672-4d3b-a187-bde5fda6533d",
            "refillable": false
          },
          "metadata": {
            "id": "1AAAbbb...ccc",
            "data": {
              "hello": "world"
            },
          },
          "timestamp": "1477578978",
          "fulfillments": [
            {
              "fid": 0,
              "input": null,
              "fulfillment": "cf:4:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkn2VnQaEWvecO1x82Qr2Va_JjFywLKIOEV1Ob9Ofkeln2K89ny2mB-s7RLNvYAVzWNiQnp18_nQEUsvwACEXTYJ",
              "owners_before": [
                "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
              ]
            }
          ]
        },
        "id": "2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e",
        "version": 1
      }]

   :resheader Content-Type: ``application/json``

   :statuscode 200: A list of transaction's containing metadata with ID ``metadata_id`` was found and returned.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``metadata_id`` querystring was not included in the request.

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

   .. literalinclude:: samples/get-tx-status-request.http
      :language: http

   **Example response**:

   .. literalinclude:: samples/get-tx-status-response.http
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

   .. sourcecode:: http

      GET /blocks/6152fbc7e0f7686512ed6b92c01e8c73ea1e3f51a7b037ac5cc8c860215e7202 HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "block":{
          "node_pubkey":"ErEeVZt8AfLbMJub25tjNxbpzzTNp3mGidL3GxGdd9bt",
            "timestamp":"1479389911",
            "transactions":[
              '<transaction1>',
              '<transaction2>'
            ],
            "voters":[
              "ErEeVZt8AfLbMJub25tjNxbpzzTNp3mGidL3GxGdd9bt"
            ]
        },
        "id":"6152fbc7e0f7686512ed6b92c01e8c73ea1e3f51a7b037ac5cc8c860215e7202",
        "signature":"53wxrEQDYk1dXzmvNSytbCfmNVnPqPkDQaTnAe8Jf43s6ssejPxezkCvUnGTnduNUmaLjhaan1iRLi3peu6s5DzA"
      }

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

   .. sourcecode:: http

      GET /blocks?tx_id=2d431...0b4b0e HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "block":{
          "node_pubkey":"ErEeVZt8AfLbMJub25tjNxbpzzTNp3mGidL3GxGdd9bt",
            "timestamp":"1479389911",
            "transactions":[
              {
                "transaction": {
                  "conditions": [
                    {
                      "cid": 0,
                      "condition": {
                        "uri": "cc:4:20:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkk:96",
                        "details": {
                          "signature": null,
                          "type": "fulfillment",
                          "type_id": 4,
                          "bitmask": 32,
                          "public_key": "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
                        }
                      },
                      "amount": 1,
                      "owners_after": [
                        "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
                      ]
                    }
                  ],
                  "operation": "CREATE",
                  "asset": {
                    "divisible": false,
                    "updatable": false,
                    "data": null,
                    "id": "aebeab22-e672-4d3b-a187-bde5fda6533d",
                    "refillable": false
                  },
                  "metadata": null,
                  "timestamp": "1477578978",
                  "fulfillments": [
                    {
                      "fid": 0,
                      "input": null,
                      "fulfillment": "cf:4:GG-pi3CeIlySZhQoJVBh9O23PzrOuhnYI7OHqIbHjkn2VnQaEWvecO1x82Qr2Va_JjFywLKIOEV1Ob9Ofkeln2K89ny2mB-s7RLNvYAVzWNiQnp18_nQEUsvwACEXTYJ",
                      "owners_before": [
                        "2ePYHfV3yS3xTxF9EE3Xjo8zPwq2RmLPFAJGQqQKc3j6"
                      ]
                    }
                  ]
                },
                "id": "2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e",
                "version": 1
              }],
            "voters":[
              "ErEeVZt8AfLbMJub25tjNxbpzzTNp3mGidL3GxGdd9bt"
            ]
        },
        "id":"6152fbc7e0f7686512ed6b92c01e8c73ea1e3f51a7b037ac5cc8c860215e7202",
        "signature":"53wxrEQDYk1dXzmvNSytbCfmNVnPqPkDQaTnAe8Jf43s6ssejPxezkCvUnGTnduNUmaLjhaan1iRLi3peu6s5DzA"
      }

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
   2. Verify the vote's signature against the vote's body (``vote.vote``) and
   ``node_pubkey``.

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
