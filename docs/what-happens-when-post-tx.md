# What happens when I post a transaction to BigchainDB test network!

Imagine I have a bigchaindb test network deployed at https://test.bigchaindb.com and I wish to post a transaction to this network.
I'd probably type something like this in my terminal:

```bash
curl -XPOST https://test.bigchaindb.com -d @tx_data.json
```

and hit enter. After a few seconds, I should see the confirmation of my transaction being successful or bein rejected. It works and that's great! But what's really going on under the hood?

This is a living document. If you spot areas that can be improved or rewritten, contributions are welcome!

Every BigchainDB instance in a BigchainDB cluster has its own unique IP address, so I can actually send my transaction to a specific BigchainDB instance if I want.
There's a [section in the HTTP API docs](https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html#determining-the-api-root-url) which explains how the IP address, domain name, and port of a particular BigchainDB instance are determined.

The details of what happens to the transaction between the client and the BigchainDB instance can vary, and aren't specific to BigchainDB.

## Arrival at the BigchainDB Instance

When the transaction arrives at the BigchainDB instance, it's in the body of an HTTP POST request. It gets picked up by an HTTP server / web server / [WSGI server]((https://www.fullstackpython.com/wsgi-servers.html)) called [Gunicorn](http://gunicorn.org/).

Gunicorn exposes a standard interface (WSGI) which enables Python applications to talk to it.
(WSGI is a Python standard. The spec is in [PEP 3333](https://www.python.org/dev/peps/pep-3333/).)
BigchainDB leverages the [Flask](http://flask.pocoo.org/) web application development framework
to simplify working with WSGI / Gunicorn.
Most of the code for BigchainDB Server's HTTP API is in the
`bigchaindb/bigchaindb/web/` directory.

Next up: Follow the route of the POST /api/v1/transactions endpoint. Point out the relevant code...

