# The HTTP Client-Server API

When you start Bigchaindb using `bigchaindb start`, an HTTP API is exposed at:

- [http://localhost:9984/api/v1/](http://localhost:9984/api/v1/)


Please note that for security reasons the server binds to `localhost:9984`.
If you want to bind the server to `0.0.0.0` we recommend you to read
[Deploying Gunicorn](http://docs.gunicorn.org/en/stable/deploy.html) and
follow the instructions to deploy it in production.

The HTTP API currently exposes two endpoints, one to get information about a
specific transaction id, and one to push a transaction to the BigchainDB
cluster. Those endpoints are documented at:

- [http://docs.bigchaindb.apiary.io/](http://docs.bigchaindb.apiary.io/)

