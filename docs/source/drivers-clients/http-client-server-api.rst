The HTTP Client-Server API
==========================

Note: The HTTP client-server API is currently quite rudimentary. For example, there is no ability to do complex queries using the HTTP API. We plan to add querying capabilities in the future. If you want to build a full-featured proof-of-concept, we suggest you use :doc:`the Python Server API <../nodes/python-server-api-examples>` for now.

When you start Bigchaindb using `bigchaindb start`, an HTTP API is exposed at the address stored in the BigchainDB node configuration settings. The default is for that address to be:

`http://localhost:9984/api/v1/ <http://localhost:9984/api/v1/>`_

but that address can be changed by changing the "API endpoint" configuration setting (e.g. in a local config file). There's more information about setting the API endpoint in :doc:`the section about Configuring a BigchainDB Node <../nodes/configuration>`.

There are other configuration settings related to the web server (serving the HTTP API). In particular, the default is for the web server socket to bind to `localhost:9984` but that can be changed (e.g. to `0.0.0.0:9984`). For more details, see the "server" settings ("bind", "workers" and "threads") in :doc:`the section about Configuring a BigchainDB Node <../nodes/configuration>`.

The HTTP API currently exposes two endpoints, one to get information about a specific transaction, and one to push a new transaction to the BigchainDB cluster.

.. http:get:: /transactions/(tx_id)

   The transaction with the transaction ID `tx_id`.

   **Example request**:

   .. sourcecode:: http

      GET /transactions/00f530d210c06671ab2de4330e3e2cf0d0b47b2826302ee25ceea9b2f47b097f HTTP/1.1
      Host: example.com
      TODO: Other headers?

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json
      TODO: Other headers?
      
      (TODO) Insert example response body here

   :statuscode 200: A transaction with that ID was found.
   :statuscode 404: A transaction with that ID was not found.


.. http:post:: /transactions/

   Push a new transaction.

   **Example request**:

   .. sourcecode:: http

      POST /transactions/ HTTP/1.1
      Host: example.com
      Content-Type: application/json
      TODO: Other headers?

      (TODO) Insert example request body here

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json
      TODO: Other headers?

      (TODO) Insert example response body here

   :statuscode 201: A new transaction was created.

(TODO) What's the response status code if the POST fails?
