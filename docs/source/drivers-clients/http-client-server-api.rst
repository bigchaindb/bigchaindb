The HTTP Client-Server API
==========================

Note: The HTTP client-server API is currently quite rudimentary. For example, there is no ability to do complex queries using the HTTP API. We plan to add querying capabilities in the future. If you want to build a full-featured proof-of-concept, we suggest you use :doc:`the Python Server API <../drivers-clients/python-server-api-examples>` for now.

When you start Bigchaindb using `bigchaindb start`, an HTTP API is exposed at the address stored in the BigchainDB node configuration settings. The default is for that address to be:

`http://localhost:9984/api/v1/ <http://localhost:9984/api/v1/>`_

but that address can be changed by changing the "API endpoint" configuration setting (e.g. in a local config file). There's more information about setting the API endpoint in :doc:`the section about BigchainDB Configuration Settings <../server-reference/configuration>`.

There are other configuration settings related to the web server (serving the HTTP API). In particular, the default is for the web server socket to bind to `localhost:9984` but that can be changed (e.g. to `0.0.0.0:9984`). For more details, see the "server" settings ("bind", "workers" and "threads") in :doc:`the section about BigchainDB Configuration Settings <../server-reference/configuration>`.

.. http:get:: /transactions/{tx_id}

   Get the transaction with the ID ``tx_id``.

   This endpoint returns only a transaction from a ``VALID`` or ``UNDECIDED`` block on ``bigchain``, if exists.

   :param tx_id: transaction ID
   :type tx_id: hex string

   **Example request**:

   .. sourcecode:: http

      GET /transactions/7ad5a4b83bc8c70c4fd7420ff3c60693ab8e6d0e3124378ca69ed5acd2578792 HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id":"7ad5a4b83bc8c70c4fd7420ff3c60693ab8e6d0e3124378ca69ed5acd2578792",
        "transaction":{
            "conditions":[
                {
                    "cid":0,
                    "condition":{
                        "details":{
                            "bitmask":32,
                            "public_key":"CwA8s2QYQBfNz4WvjEwmJi83zYr7JhxRhidx6uZ5KBVd",
                            "signature":null,
                            "type":"fulfillment",
                            "type_id":4
                        },
                        "uri":"cc:4:20:sVA_3p8gvl8yRFNTomqm6MaavKewka6dGYcFAuPrRXQ:96"
                    },
                    "owners_after":[
                        "CwA8s2QYQBfNz4WvjEwmJi83zYr7JhxRhidx6uZ5KBVd"
                    ]
                }
            ],
            "data":{
                "payload":null,
                "uuid":"a9999d69-6cde-4b80-819d-ed57f6abe257"
            },
            "fulfillments":[
                {
                    "owners_before":[
                        "JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE"
                    ],
                    "fid":0,
                    "fulfillment":"cf:4:__Y_Um6H73iwPe6ejWXEw930SQhqVGjtAHTXilPp0P01vE_Cx6zs3GJVoO1jhPL18C94PIVkLTGMUB2aKC9qsbIb3w8ejpOf0_I3OCuTbPdkd6r2lKMeVftMyMxkeWoM",
                    "input":{
                        "cid":0,
                        "txid":"598ce4e9a29837a1c6fc337ee4a41b61c20ad25d01646754c825b1116abd8761"
                    }
                }
            ],
            "operation":"TRANSFER",
            "timestamp":"1471423869",
            "version":1
         }
      }

   :statuscode 200: A transaction with that ID was found.
   :statuscode 404: A transaction with that ID was not found.

.. http:post:: /transactions/

   Push a new transaction.

   **Example request**:

   .. sourcecode:: http

      POST /transactions/ HTTP/1.1
      Host: example.com
      Content-Type: application/json

      {
        "id":"7ad5a4b83bc8c70c4fd7420ff3c60693ab8e6d0e3124378ca69ed5acd2578792",
        "transaction":{
            "conditions":[
                {
                    "cid":0,
                    "condition":{
                        "details":{
                            "bitmask":32,
                            "public_key":"CwA8s2QYQBfNz4WvjEwmJi83zYr7JhxRhidx6uZ5KBVd",
                            "signature":null,
                            "type":"fulfillment",
                            "type_id":4
                        },
                        "uri":"cc:4:20:sVA_3p8gvl8yRFNTomqm6MaavKewka6dGYcFAuPrRXQ:96"
                    },
                    "owners_after":[
                        "CwA8s2QYQBfNz4WvjEwmJi83zYr7JhxRhidx6uZ5KBVd"
                    ]
                }
            ],
            "data":{
                "payload":null,
                "uuid":"a9999d69-6cde-4b80-819d-ed57f6abe257"
            },
            "fulfillments":[
                {
                    "owners_before":[
                        "JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE"
                    ],
                    "fid":0,
                    "fulfillment":"cf:4:__Y_Um6H73iwPe6ejWXEw930SQhqVGjtAHTXilPp0P01vE_Cx6zs3GJVoO1jhPL18C94PIVkLTGMUB2aKC9qsbIb3w8ejpOf0_I3OCuTbPdkd6r2lKMeVftMyMxkeWoM",
                    "input":{
                        "cid":0,
                        "txid":"598ce4e9a29837a1c6fc337ee4a41b61c20ad25d01646754c825b1116abd8761"
                    }
                }
            ],
            "operation":"TRANSFER",
            "timestamp":"1471423869",
            "version":1
         }
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "assignee":"4XYfCbabAWVUCbjTmRTFEu2sc3dFEdkse4r6X498B1s8",
        "id":"7ad5a4b83bc8c70c4fd7420ff3c60693ab8e6d0e3124378ca69ed5acd2578792",
        "transaction":{
            "conditions":[
                {
                    "cid":0,
                    "condition":{
                        "details":{
                            "bitmask":32,
                            "public_key":"CwA8s2QYQBfNz4WvjEwmJi83zYr7JhxRhidx6uZ5KBVd",
                            "signature":null,
                            "type":"fulfillment",
                            "type_id":4
                        },
                        "uri":"cc:4:20:sVA_3p8gvl8yRFNTomqm6MaavKewka6dGYcFAuPrRXQ:96"
                    },
                    "owners_after":[
                        "CwA8s2QYQBfNz4WvjEwmJi83zYr7JhxRhidx6uZ5KBVd"
                    ]
                }
            ],
            "data":{
                "payload":null,
                "uuid":"a9999d69-6cde-4b80-819d-ed57f6abe257"
            },
            "fulfillments":[
                {
                    "owners_before":[
                        "JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE"
                    ],
                    "fid":0,
                    "fulfillment":"cf:4:__Y_Um6H73iwPe6ejWXEw930SQhqVGjtAHTXilPp0P01vE_Cx6zs3GJVoO1jhPL18C94PIVkLTGMUB2aKC9qsbIb3w8ejpOf0_I3OCuTbPdkd6r2lKMeVftMyMxkeWoM",
                    "input":{
                        "cid":0,
                        "txid":"598ce4e9a29837a1c6fc337ee4a41b61c20ad25d01646754c825b1116abd8761"
                    }
                }
            ],
            "operation":"TRANSFER",
            "timestamp":"1471423869",
            "version":1
        }
      }

   :statuscode 201: A new transaction was created.
   :statuscode 400: The transaction was invalid and not created.

   **Disclaimer**

   ``CREATE`` transactions are treated differently from ``TRANSFER`` assets.
   The reason is that a ``CREATE`` transaction needs to be signed by a federation node and not by the client.

   The following python snippet in a client can be used to generate ``CREATE`` transactions before they can be pushed to the API server:

   .. code-block:: python

       from bigchaindb import util
       tx = util.create_and_sign_tx(my_privkey, my_pubkey, my_pubkey, None, 'CREATE')

   When POSTing ``tx`` to the API, the ``CREATE`` transaction will be signed by a federation node.

   A ``TRANSFER`` transaction, that takes an existing input transaction to change ownership can be generated in multiple ways:

   .. code-block:: python

       from bigchaindb import util, Bigchain
       tx = util.create_and_sign_tx(my_privkey, my_pubkey, other_pubkey, input_tx, 'TRANSFER')
       # or
       b = Bigchain()
       tx_unsigned = b.create_transaction(my_pubkey, other_pubkey, input_tx, 'TRANSFER')
       tx = b.sign_transaction(tx_unsigned, my_privkey)

   More information on generating transactions can be found in the `Python server API examples <python-server-api-examples.html>`_

.. http:get:: /transactions/{tx_id}/status

   Get the status of a transaction with the ID ``tx_id``.

   This endpoint returns the status of a transaction if exists.

   Possible values are ``valid``, ``invalid``, ``undecided`` or ``backlog``.

   :param tx_id: transaction ID
   :type tx_id: hex string

   **Example request**:

   .. sourcecode:: http

      GET /transactions/7ad5a4b83bc8c70c4fd7420ff3c60693ab8e6d0e3124378ca69ed5acd2578792/status HTTP/1.1
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


.. http:get:: /transactions/unspents/{owner_id}

   Get a list of unspent transactions of an owner with public key ``owner_id``.

   :param owner_id: public key of the owner
   :type owner_id: base58 string

   **Example request**:

   .. sourcecode:: http

      GET /transactions/unspents/JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE HTTP/1.1
      Host: example.com

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
         {"cid": 0, "txid": "91ccac5037ed09332473f6e08a4b57260ac677ddb5985ac37b9a42ca21979cf6"},
         {"cid": 0, "txid": "03aa60ae9acde5ede7c8c6fc5efe23c61bfd3d576d69ba425f0a718120fa2a04"},
         {"cid": 0, "txid": "143a086e7888d32a81753e3842989c006948c639bbf6edd228bf95389b1e0af9"}
      ]

   :statuscode 200: A list of transaction ids or an empty list was returned.
