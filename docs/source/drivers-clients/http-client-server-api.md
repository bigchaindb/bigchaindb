# The HTTP Client-Server API

Note: The HTTP client-server API is currently quite rudimentary. For example, there is no ability to do complex queries using the HTTP API. We plan to add querying capabilities in the future. If you want to build a full-featured proof-of-concept, we suggest you use [the Python server API](../nodes/python-server-api-examples.html) for now.

When you start Bigchaindb using `bigchaindb start`, an HTTP API is exposed at the address stored in the BigchainDB node configuration settings. The default is for that address to be:

[http://localhost:9984/api/v1/](http://localhost:9984/api/v1/)

but that address can be changed by changing the "API endpoint" configuration setting (e.g. in a local config file). There's more information about setting the API endpoint in [the section about Configuring a BigchainDB Node](../nodes/configuration.html).

There are other configuration settings related to the web server (serving the HTTP API). In particular, the default is for the web server socket to bind to `localhost:9984` but that can be changed (e.g. to `0.0.0.0:9984`). For more details, see the "server" settings ("bind", "workers" and "threads") in [the section about Configuring a BigchainDB Node](../nodes/configuration.html).

The HTTP API currently exposes two endpoints, one to get information about a
specific transaction id, and one to push a transaction to the BigchainDB
cluster. Those endpoints are documented at:

[http://docs.bigchaindb.apiary.io/](http://docs.bigchaindb.apiary.io/)
