# The HTTP Client-Server API

Note: The HTTP client-server API is currently quite rudimentary. For example, there is no ability to do complex queries using the HTTP API. We plan to add querying capabilities in the future. If you want to build a full-featured proof-of-concept, we suggest you use [the Python server API](../nodes/python-server-api-examples.html) for now.

When you start Bigchaindb using `bigchaindb start`, an HTTP API is exposed at:

[http://localhost:9984/api/v1/](http://localhost:9984/api/v1/)

For security reasons, the server binds to `localhost:9984`.
If you want to bind the server to `0.0.0.0` we recommend you to read
[Deploying Gunicorn](http://docs.gunicorn.org/en/stable/deploy.html) and
follow the instructions to deploy it in production.

The HTTP API currently exposes two endpoints, one to get information about a
specific transaction id, and one to push a transaction to the BigchainDB
cluster. Those endpoints are documented at:

[http://docs.bigchaindb.apiary.io/](http://docs.bigchaindb.apiary.io/)
