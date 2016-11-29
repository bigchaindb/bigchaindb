The HTTP Client-Server API
==========================

.. note::

   The HTTP client-server API is currently quite rudimentary. For example,
   there is no ability to do complex queries using the HTTP API. We plan to add
   querying capabilities in the future.

When you start Bigchaindb using `bigchaindb start`, an HTTP API is exposed at
the address stored in the BigchainDB node configuration settings. The default
is:

`http://localhost:9984/api/v1/ <http://localhost:9984/api/v1/>`_

but that address can be changed by changing the "API endpoint" configuration
setting (e.g. in a local config file). There's more information about setting
the API endpoint in :doc:`the section about BigchainDB Configuration Settings
<../server-reference/configuration>`.

There are other configuration settings related to the web server (serving the
HTTP API). In particular, the default is for the web server socket to bind to
``localhost:9984`` but that can be changed (e.g. to ``0.0.0.0:9984``). For more
details, see the "server" settings ("bind", "workers" and "threads") in
:doc:`the section about BigchainDB Configuration Settings
<../server-reference/configuration>`.


API Root
--------

If you send an HTTP GET request to e.g. ``http://localhost:9984`` (with no
``/api/v1/`` on the end), then you should get an HTTP response with something
like the following in the body:

.. code-block:: json

    {
      "api_endpoint": "http://localhost:9984/api/v1",
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

   Note: The posted transaction should be a valid and signed `transaction
   <https://bigchaindb.readthedocs.io/en/latest/data-models/transaction-model.html>`_.
   The steps to build a valid transaction are beyond the scope of this page.
   One would normally use a driver such as the `BigchainDB Python Driver
   <https://docs.bigchaindb.com/projects/py-driver/en/latest/index.html>`_ to
   build a valid transaction. The exact contents of a valid transaction depend 
   on the associated public/private keypairs.

   **Example request**:

   .. sourcecode:: http

      POST /transactions/ HTTP/1.1
      Host: example.com
      Content-Type: application/json

      {
        "transaction": {
          "conditions": [
            {
              "cid": 0,
              "condition": {
                "uri": "cc:4:20:fSlVCKNSzSl0meiwwuUk5JpJ0KLlECTqbd25KyQefFY:96",
                "details": {
                  "signature": null,
                  "type": "fulfillment",
                  "type_id": 4,
                  "bitmask": 32,
                  "public_key": "9RaWxppkP9UyYWA7NJb5FcgkzfJNPfvPX3FCNw2T5Pwb"
                }
              },
              "amount": 1,
              "owners_after": [
                "9RaWxppkP9UyYWA7NJb5FcgkzfJNPfvPX3FCNw2T5Pwb"
              ]
            }
          ],
          "operation": "CREATE",
          "asset": {
            "divisible": false,
            "updatable": false,
            "data": null,
            "id": "b57801f8-b865-4360-9d1a-3e3009f5ce01",
            "refillable": false
          },
          "metadata": null,
          "fulfillments": [
            {
              "fid": 0,
              "input": null,
              "fulfillment": "cf:4:fSlVCKNSzSl0meiwwuUk5JpJ0KLlECTqbd25KyQefFaf8bQVH1gesZGEGZepCE8_kgo-UfBrCHPlvBsnAsfq56GWjrLTyZ9NXISwcyJ3zmygnVhCMG8xzE6c9fj1-6wK",
              "owners_before": [
                  "9RaWxppkP9UyYWA7NJb5FcgkzfJNPfvPX3FCNw2T5Pwb"
              ]
            }
          ]
        },
        "id": "65f1f69b6ebf995a7b2c5ae8a6fb480ce20f0e8f1eb1d77d75f37ab00ccdeec3",
        "version": 1
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": "65f1f69b6ebf995a7b2c5ae8a6fb480ce20f0e8f1eb1d77d75f37ab00ccdeec3",
        "version": 1,
        "transaction": {
          "conditions": [
            {
              "amount": 1,
              "condition": {
                "uri": "cc:4:20:fSlVCKNSzSl0meiwwuUk5JpJ0KLlECTqbd25KyQefFY:96",
                "details": {
                  "signature": null,
                  "type_id": 4,
                  "type": "fulfillment",
                  "bitmask": 32,
                  "public_key": "9RaWxppkP9UyYWA7NJb5FcgkzfJNPfvPX3FCNw2T5Pwb"
                }
              },
              "owners_after": [
                "9RaWxppkP9UyYWA7NJb5FcgkzfJNPfvPX3FCNw2T5Pwb"
              ],
              "cid": 0
            }
          ],
          "fulfillments": [
            {
              "input": null,
              "fulfillment": "cf:4:fSlVCKNSzSl0meiwwuUk5JpJ0KLlECTqbd25KyQefFaf8bQVH1gesZGEGZepCE8_kgo-UfBrCHPlvBsnAsfq56GWjrLTyZ9NXISwcyJ3zmygnVhCMG8xzE6c9fj1-6wK",
              "fid": 0,
              "owners_before": [
                "9RaWxppkP9UyYWA7NJb5FcgkzfJNPfvPX3FCNw2T5Pwb"
              ]
            }
          ],
          "operation": "CREATE",
          "asset": {
            "updatable": false,
            "refillable": false,
            "divisible": false,
            "data": null,
            "id": "b57801f8-b865-4360-9d1a-3e3009f5ce01"
          },
          "metadata": null
        }
      }

   :statuscode 201: A new transaction was created.
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

   .. sourcecode:: http

      GET /transactions/65f1f69b6ebf995a7b2c5ae8a6fb480ce20f0e8f1eb1d77d75f37ab00ccdeec3/status HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "valid"
      }

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

   .. sourcecode:: http

      GET /transactions/65f1f69b6ebf995a7b2c5ae8a6fb480ce20f0e8f1eb1d77d75f37ab00ccdeec3 HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "transaction": {
          "conditions": [
            {
              "cid": 0,
              "condition": {
                "uri": "cc:4:20:fSlVCKNSzSl0meiwwuUk5JpJ0KLlECTqbd25KyQefFY:96",
                "details": {
                  "signature": null,
                  "type": "fulfillment",
                  "type_id": 4,
                  "bitmask": 32,
                  "public_key": "9RaWxppkP9UyYWA7NJb5FcgkzfJNPfvPX3FCNw2T5Pwb"
                }
              },
              "amount": 1,
              "owners_after": [
                "9RaWxppkP9UyYWA7NJb5FcgkzfJNPfvPX3FCNw2T5Pwb"
              ]
            }
          ],
          "operation": "CREATE",
          "asset": {
            "divisible": false,
            "updatable": false,
            "data": null,
            "id": "b57801f8-b865-4360-9d1a-3e3009f5ce01",
            "refillable": false
          },
          "metadata": null,
          "fulfillments": [
            {
              "fid": 0,
              "input": null,
              "fulfillment": "cf:4:fSlVCKNSzSl0meiwwuUk5JpJ0KLlECTqbd25KyQefFaf8bQVH1gesZGEGZepCE8_kgo-UfBrCHPlvBsnAsfq56GWjrLTyZ9NXISwcyJ3zmygnVhCMG8xzE6c9fj1-6wK",
              "owners_before": [
                "9RaWxppkP9UyYWA7NJb5FcgkzfJNPfvPX3FCNw2T5Pwb"
              ]
            }
          ]
        },
        "id": "65f1f69b6ebf995a7b2c5ae8a6fb480ce20f0e8f1eb1d77d75f37ab00ccdeec3",
        "version": 1
      }

   :statuscode 200: A transaction with that ID was found.
   :statuscode 404: A transaction with that ID was not found.


GET /unspents/
-------------------------

.. note::

   This endpoint (unspents) is not yet implemented. We published it here for preview and comment.
   

.. http:get:: /unspents?owner_after={owner_after}

   Get a list of links to transactions' conditions that have not been used in
   a previous transaction and could hence be called unspent conditions/outputs
   (or simply: unspents).

   This endpoint will return a ``HTTP 400 Bad Request`` if the querystring
   ``owner_after`` happens to not be defined in the request.

   Note that if unspents for a certain ``owner_after`` have not been found by
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
        '../transactions/2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e/conditions/0',
        '../transactions/2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e/conditions/1'
      ]

   :statuscode 200: A list of outputs were found and returned in the body of the response.
   :statuscode 400: The request wasn't understood by the server, e.g. the ``owner_after`` querystring was not included in the request.
