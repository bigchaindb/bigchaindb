# Using a Reverse Proxy

You may want to:

* rate limit inbound HTTP requests,
* authenticate/authorize inbound HTTP requests,
* block requests with an HTTP request body that's too large, or
* enable HTTPS (TLS) between your users and your node.

While we could have built all that into BigchainDB Server,
we didn't, because you can do all that (and more)
using a reverse proxy such as NGINX or HAProxy.
(You would put it in front of your BigchainDB Server,
so that all inbound HTTP requests would arrive
at the reverse proxy before *maybe* being proxied
onwards to your BigchainDB Server.)
For detailed instructions, see the documentation
for your reverse proxy.

Below, we note how a reverse proxy can be used
to do some BigchainDB-specific things.

You may also be interested in
[our NGINX configuration file template](https://github.com/bigchaindb/nginx_3scale/blob/master/nginx.conf.template)
(open source, on GitHub).


## Enforcing a Max Transaction Size

The BigchainDB HTTP API has several endpoints,
but only one of them, the `POST /transactions` endpoint,
expects a non-empty HTTP request body:
the transaction (JSON) being submitted by the user.

If you want to enforce a maximum-allowed transaction size
(discarding any that are larger),
then you can do so by configuring a maximum request body size
in your reverse proxy.
For example, NGINX has the `client_max_body_size`
configuration setting. You could set it to 15 kB
with the following line in your NGINX config file:

```text
client_max_body_size 15k;
```

For more information, see
[the NGINX docs about client_max_body_size](https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size).

Note: By enforcing a maximum transaction size, you
[indirectly enforce a maximum crypto-conditions complexity](https://github.com/bigchaindb/bigchaindb/issues/356#issuecomment-288085251).


**Aside: Why 15 kB?**

Both [RethinkDB](https://rethinkdb.com/limitations/) and
[MongoDB have a maximum document size of 16 MB](https://docs.mongodb.com/manual/reference/limits/#limit-bson-document-size).
In BigchainDB, the biggest documents are the blocks.
A BigchainDB block can contain up to 1000 transactions,
plus some other data (e.g. the timestamp).
If we ignore the other data as negligible relative to all the transactions,
then a block of size 16 MB
will have an average transaction size of (16 MB)/1000 = 16 kB.
Therefore by limiting the max transaction size to 15 kB,
you can be fairly sure that no blocks will ever be
bigger than 16 MB.

Note: Technically, the documents that MongoDB stores aren't the JSON
that BigchainDB users think of; they're JSON converted to BSON.
Moreover, [one can use GridFS with MongoDB to store larger documents](https://docs.mongodb.com/manual/core/gridfs/).
Therefore the above calculation shoud be seen as a rough guide,
not the last word.
