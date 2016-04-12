# The HTTP Client-Server API

When you start Bigchaindb using `bigchaindb start`, an HTTP API is exposed at:

- [http://localhost:9984/api/v1/](http://localhost:9984/api/v1/)


Please note that by default the server binds to `0.0.0.0:9984`, hence the API
is exposed to the world.

The HTTP API currently exposes two endpoints, one to get information about a
specific transaction id, and one to push a transaction to the BigchainDB
cluster. Those endpoints are documented at:

- [http://docs.bigchaindb.apiary.io/](http://docs.bigchaindb.apiary.io/)

