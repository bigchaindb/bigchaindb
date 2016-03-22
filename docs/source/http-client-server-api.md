# The HTTP Client-Server API

When you start Bigchaindb using `bigchaindb start`, an HTTP API is exposed at:

[http://localhost:5000/api/v1/](http://localhost:5000/api/v1/)

Right now, that API can only be accessed from localhost (i.e. not remotely). In the future, we'll enable remote access and explain how that works. See [Issue #149](https://github.com/bigchaindb/bigchaindb/issues/149) on GitHub.

The HTTP API currently exposes two endpoints, one to get information about a specific transaction id, and one to push a transaction to the BigchainDB cluster. Those endpoints are documented at:

[http://docs.bigchaindb.apiary.io/](http://docs.bigchaindb.apiary.io/)
