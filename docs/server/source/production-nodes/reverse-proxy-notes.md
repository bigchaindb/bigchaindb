<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

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
the transaction being submitted by the user.

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
