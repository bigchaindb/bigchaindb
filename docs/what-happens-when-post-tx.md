# What happens when I post a transaction to BigchainDB test network!

Imagine I have a bigchaindb test network deployed at https://test.bigchaindb.com and I wish to post a transaction to this network.
I'd probably type something like this in my terminal:

```bash
curl -XPOST https://test.bigchaindb.com/api/v1/transactions -d @tx_data.json
```

and hit enter. After a few seconds, I should see the confirmation of my transaction being successful or bein rejected. It works and that's great! But what's really going on under the hood?

This is a living document. If you spot areas that can be improved or rewritten, contributions are welcome!

Every BigchainDB instance in a BigchainDB cluster has its own unique IP address, so I can actually send my transaction to a specific BigchainDB instance if I want. There's a [section in the HTTP API docs](https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html#determining-the-api-root-url) which explains how the IP address, domain name, and port of a particular BigchainDB instance are determined.

The details of what happens to the transaction between the client and the BigchainDB instance can vary, and aren't specific to BigchainDB.

## Arrival at the BigchainDB Instance

When the transaction arrives at the BigchainDB instance, it's in the body of an HTTP POST request. It gets picked up by an HTTP server / web server / [WSGI server]((https://www.fullstackpython.com/wsgi-servers.html)) called [Gunicorn](http://gunicorn.org/).

Gunicorn exposes a standard interface ([WSGI](https://www.fullstackpython.com/wsgi-servers.html)) which enables Python applications to talk to it. (WSGI is a Python standard. The spec is in [PEP 3333](https://www.python.org/dev/peps/pep-3333/).) BigchainDB leverages the [Flask](http://flask.pocoo.org/) web application development framework to simplify working with WSGI / Gunicorn. Most (or all?) of the code for BigchainDB Server's HTTP API is in the `bigchaindb/bigchaindb/web/` directory.

Where's the Python code that handles our `POST /api/v1/transactions` request?

## Routing the HTTP POST Request

First we need to find out how `/api/v1/transactions` gets _routed_. That's set in the file `bigchaindb/bigchaindb/web/routes.py`:

```python
API_SECTIONS = [
    (None, [r('/', info.RootIndex)]),
    ('/api/v1/', ROUTES_API_V1),
]
```

and

```python
    r('transactions', tx.TransactionListApi),
```

where `tx` is `transactions` in `bigchaindb.web.views`. Therefore our `POST /api/v1/transactions` request gets routed to the `post()` method in the `bigchaindb.web.views.transactions.TransactionListApi` class.

## What happens to the Routed HTTP POST Request?

The `bigchaindb.web.views.transactions.TransactionListApi` class and method are defined in the file `bigchaindb/bigchaindb/web/views/transactions.py`. You should read that method definition. Here's a summary:

- It defines the `mode` query parameter, its allowed values, and its default value ('broadcast_tx_async'). Because we didn't include the `mode` parameter in the request, it gets the default value.
- It sets `mode = str(args['mode'])`
- It gets the content of the body of the HTTP POST request as a Python dict, using `tx = request.get_json(force=True)`
- It tries to convert that Python dict to a BigchainDB Transaction object, using `tx_obj = Transaction.from_dict(tx)`
  - If a SchemaValidationError exception is raised, it sends back an HTTP response about an invalid transaction schema, with HTTP status code 400.
  - If a ValidationError exception is raised, it sends back an HTTP response about an invalid transaction, with HTTP status code 400.

Question: Why can `tx_obj = Transaction.from_dict(tx)` raise validation-related exceptions? If the JSON schema is wrong, then it can't build a proper Transaction object. That makes sense. But why can a ValidationError be raised? Shouldn't non-schema-related validation be a separate concern? Sylvain has noted this in some issues.

It then tries `bigchain.validate_transaction(tx_obj)`. That can also raise a ValidationError, and if it does, it sends back an HTTP response about an invalid transaction, with HTTP status code 400. If no exception is raised, then it does `bigchain.write_transaction(tx_obj, mode)`. We'll follow what that does in the next section.

Questions: I think this method is blocked for now until `bigchain.write_transaction(tx_obj, mode)` finishes. Is that right? What if it never finishes, or some timeout time passes?

Once the method gets unblocked, it wraps up by sending back a response where the body is the tx (jsonified), and the status code is 202.

Question: Should we _always_ be sending back HTTP status code 202? What if `mode` was `commit`? What if the transaction got rejected as invalid by all the other nodes (except this one)? HTTP status code 202 is supposed to mean:

> 202 Accepted. The request has been accepted for processing, but the processing has not been completed. The request might or might not eventually be acted upon, as it might be disallowed when processing actually takes place.

## Unpacking bigchain.write_transaction(tx_obj, mode)

Coming soon!
