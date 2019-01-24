<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Configuration Settings

Every BigchainDB Server configuration setting has two names: a config-file name and an environment variable name. For example, one of the settings has the config-file name `database.host` and the environment variable name `BIGCHAINDB_DATABASE_HOST`. Here are some more examples:

`database.port` ↔ `BIGCHAINDB_DATABASE_PORT`

`database.keyfile_passphrase` ↔ `BIGCHAINDB_DATABASE_KEYFILE_PASSPHRASE`

`server.bind` ↔ `BIGCHAINDB_SERVER_BIND`

The value of each setting is determined according to the following rules:

* If it's set by an environment variable, then use that value
* Otherwise, if it's set in a local config file, then use that value
* Otherwise, use the default value

The local config file is `$HOME/.bigchaindb` by default (a file which might not even exist), but you can tell BigchainDB to use a different file by using the `-c` command-line option, e.g. `bigchaindb -c path/to/config_file.json start`
or using the `BIGCHAINDB_CONFIG_PATH` environment variable, e.g. `BIGHAINDB_CONFIG_PATH=.my_bigchaindb_config bigchaindb start`.
Note that the `-c` command line option will always take precedence if both the `BIGCHAINDB_CONFIG_PATH` and the `-c` command line option are used.

You can read the current default values in the file [bigchaindb/\_\_init\_\_.py](https://github.com/bigchaindb/bigchaindb/blob/master/bigchaindb/__init__.py). (The link is to the latest version.)

Running `bigchaindb -y configure localmongodb` will generate a local config file in `$HOME/.bigchaindb` with all the default values.

## database.*

The settings with names of the form `database.*` are for the backend database
(currently only MongoDB). They are:

* `database.backend` can only be `localmongodb`, currently.
* `database.host` is the hostname (FQDN) of the backend database.
* `database.port` is self-explanatory.
* `database.name` is a user-chosen name for the database inside MongoDB, e.g. `bigchain`.
* `database.connection_timeout` is the maximum number of milliseconds that BigchainDB will wait before giving up on one attempt to connect to the backend database.
* `database.max_tries` is the maximum number of times that BigchainDB will try to establish a connection with the backend database. If 0, then it will try forever.
* `database.replicaset` is the name of the MongoDB replica set. The default value is `null` because in BigchainDB 2.0+, each BigchainDB node has its own independent MongoDB database and no replica set is necessary. Replica set must already exist if this option is configured, BigchainDB will not create it.
* `database.ssl` must be `true` or `false`. It tells BigchainDB Server whether it should connect to MongoDB using TLS/SSL or not. The default value is `false`.

There are three ways for BigchainDB Server to authenticate itself with MongoDB (or a specific MongoDB database): no authentication, username/password, and x.509 certificate authentication.

**No Authentication**

If you use all the default BigchainDB configuration settings, then no authentication will be used.

**Username/Password Authentication**

To use username/password authentication, a MongoDB instance must already be running somewhere (maybe in another machine), it must already have a database for use by BigchainDB (usually named `bigchain`, which is the default `database.name`), and that database must already have a "readWrite" user with associated username and password. To create such a user, login to your MongoDB instance as Admin and run the following commands:

```text
use <database.name>
db.createUser({user: "<database.login>", pwd: "<database.password>", roles: [{role: "readWrite", db: "<database.name>"}]})
```

* `database.login` is the user's username.
* `database.password` is the user's password, given in plaintext.
* `database.ca_cert`, `database.certfile`, `database.keyfile`, `database.crlfile`, and `database.keyfile_passphrase` are not used so they can have their default values.

**x.509 Certificate Authentication**

To use x.509 certificate authentication, a MongoDB instance must be running somewhere (maybe in another machine), it must already have a database for use by BigchainDB (usually named `bigchain`, which is the default `database.name`), and that database must be set up to use x.509 authentication. See the MongoDB docs about how to do that.

* `database.login` is the user's username.
* `database.password` isn't used so the default value (`null`) is fine.
* `database.ca_cert`, `database.certfile`, `database.keyfile` and `database.crlfile` are the paths to the CA, signed certificate, private key and certificate revocation list files respectively.
* `database.keyfile_passphrase` is the private key decryption passphrase, specified in plaintext.

**Example using environment variables**

```text
export BIGCHAINDB_DATABASE_BACKEND=localmongodb
export BIGCHAINDB_DATABASE_HOST=localhost
export BIGCHAINDB_DATABASE_PORT=27017
export BIGCHAINDB_DATABASE_NAME=database8
export BIGCHAINDB_DATABASE_CONNECTION_TIMEOUT=5000
export BIGCHAINDB_DATABASE_MAX_TRIES=3
```

**Default values**

If (no environment variables were set and there's no local config file), or you used `bigchaindb -y configure localmongodb` to create a default local config file for a `localmongodb` backend, then the defaults will be:

```js
"database": {
    "backend": "localmongodb",
    "host": "localhost",
    "port": 27017,
    "name": "bigchain",
    "connection_timeout": 5000,
    "max_tries": 3,
    "replicaset": null,
    "login": null,
    "password": null
    "ssl": false,
    "ca_cert": null,
    "certfile": null,
    "keyfile": null,
    "crlfile": null,
    "keyfile_passphrase": null,
}
```

## server.*

`server.bind`, `server.loglevel` and `server.workers`
are settings for the [Gunicorn HTTP server](http://gunicorn.org/), which is used to serve the [HTTP client-server API](../http-client-server-api).

`server.bind` is where to bind the Gunicorn HTTP server socket. It's a string. It can be any valid value for [Gunicorn's bind setting](http://docs.gunicorn.org/en/stable/settings.html#bind). For example:

* If you want to allow IPv4 connections from anyone, on port 9984, use `0.0.0.0:9984`
* If you want to allow IPv6 connections from anyone, on port 9984, use `[::]:9984`

In a production setting, we recommend you use Gunicorn behind a reverse proxy server such as NGINX. If Gunicorn and the reverse proxy are running on the same machine, then you can use `localhost:9984` (the default value), meaning Gunicorn will talk to the reverse proxy on port 9984. The reverse proxy could then be bound to port 80 (for HTTP) or port 443 (for HTTPS), so that external clients would connect using that port. For example:

[External clients]---(port 443)---[NGINX]---(port 9984)---[Gunicorn / BigchainDB Server]

If Gunicorn and the reverse proxy are running on different machines, then `server.bind` should be `hostname:9984`, where hostname is the IP address or [FQDN](https://en.wikipedia.org/wiki/Fully_qualified_domain_name) of the reverse proxy.

There's [more information about deploying behind a reverse proxy in the Gunicorn documentation](http://docs.gunicorn.org/en/stable/deploy.html). (They call it a proxy.)

`server.loglevel` sets the log level of Gunicorn's Error log outputs. See
[Gunicorn's documentation](http://docs.gunicorn.org/en/latest/settings.html#loglevel)
for more information.

`server.workers` is [the number of worker processes](http://docs.gunicorn.org/en/stable/settings.html#workers) for handling requests. If set to `None`, the value will be (2 × cpu_count + 1). Each worker process has a single thread. The HTTP server will be able to handle `server.workers` requests simultaneously.

**Example using environment variables**

```text
export BIGCHAINDB_SERVER_BIND=0.0.0.0:9984
export BIGCHAINDB_SERVER_LOGLEVEL=debug
export BIGCHAINDB_SERVER_WORKERS=5
```

**Example config file snippet**

```js
"server": {
    "bind": "0.0.0.0:9984",
    "loglevel": "debug",
    "workers": 5,
}
```

**Default values (from a config file)**

```js
"server": {
    "bind": "localhost:9984",
    "loglevel": "info",
    "workers": null,
}
```

## wsserver.*


### wsserver.scheme, wsserver.host and wsserver.port

These settings are for the
[aiohttp server](https://aiohttp.readthedocs.io/en/stable/index.html),
which is used to serve the
[WebSocket Event Stream API](../events/websocket-event-stream-api).
`wsserver.scheme` should be either `"ws"` or `"wss"`
(but setting it to `"wss"` does *not* enable SSL/TLS).
`wsserver.host` is where to bind the aiohttp server socket and
`wsserver.port` is the corresponding port.
If you want to allow connections from anyone, on port 9985,
set `wsserver.host` to 0.0.0.0 and `wsserver.port` to 9985.

**Example using environment variables**

```text
export BIGCHAINDB_WSSERVER_SCHEME=ws
export BIGCHAINDB_WSSERVER_HOST=0.0.0.0
export BIGCHAINDB_WSSERVER_PORT=9985
```

**Example config file snippet**

```js
"wsserver": {
    "scheme": "wss",
    "host": "0.0.0.0",
    "port": 65000
}
```

**Default values (from a config file)**

```js
"wsserver": {
    "scheme": "ws",
    "host": "localhost",
    "port": 9985
}
```

### wsserver.advertised_scheme, wsserver.advertised_host and wsserver.advertised_port

These settings are for the advertising the Websocket URL to external clients in
the root API endpoint. These configurations might be useful if your deployment
is hosted behind a firewall, NAT, etc. where the exposed public IP or domain is
different from where BigchainDB is running.

**Example using environment variables**

```text
export BIGCHAINDB_WSSERVER_ADVERTISED_SCHEME=wss
export BIGCHAINDB_WSSERVER_ADVERTISED_HOST=mybigchaindb.com
export BIGCHAINDB_WSSERVER_ADVERTISED_PORT=443
```

**Example config file snippet**

```js
"wsserver": {
    "advertised_scheme": "wss",
    "advertised_host": "mybigchaindb.com",
    "advertised_port": 443
}
```

**Default values (from a config file)**

```js
"wsserver": {
    "advertised_scheme": "ws",
    "advertised_host": "localhost",
    "advertised_port": 9985
}
```

## log.*

The `log.*` settings are to configure logging.

**Example**

```js
{
    "log": {
        "file": "/var/log/bigchaindb.log",
        "error_file": "/var/log/bigchaindb-errors.log",
        "level_console": "info",
        "level_logfile": "info",
        "datefmt_console": "%Y-%m-%d %H:%M:%S",
        "datefmt_logfile": "%Y-%m-%d %H:%M:%S",
        "fmt_console": "%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
        "fmt_logfile": "%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
        "granular_levels": {}
}
```

**Default values**

```js
{
    "log": {
        "file": "~/bigchaindb.log",
        "error_file": "~/bigchaindb-errors.log",
        "level_console": "info",
        "level_logfile": "info",
        "datefmt_console": "%Y-%m-%d %H:%M:%S",
        "datefmt_logfile": "%Y-%m-%d %H:%M:%S",
        "fmt_logfile": "[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s (%(processName)-10s - pid: %(process)d)",
        "fmt_console": "[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s (%(processName)-10s - pid: %(process)d)",
        "granular_levels": {}
}
```

### log.file

The full path to the file where logs should be written.
The user running `bigchaindb` must have write access to the
specified path.

**Log rotation:** Log files have a size limit of about 200 MB
and will be rotated up to five times.
For example, if `log.file` is set to `"~/bigchain.log"`, then
logs would always be written to `bigchain.log`. Each time the file
`bigchain.log` reaches 200 MB it will be closed and renamed
`bigchain.log.1`. If `bigchain.log.1` and `bigchain.log.2` already exist they
would be renamed `bigchain.log.2` and `bigchain.log.3`. This pattern would be
applied up to `bigchain.log.5` after which `bigchain.log.5` would be
overwritten by `bigchain.log.4`, thus ending the rotation cycle of whatever
logs were in `bigchain.log.5`.

### log.error_file

Similar to `log.file` (see above), this is the
full path to the file where error logs should be written.

### log.level_console

The log level used to log to the console. Possible allowed values are the ones
defined by [Python](https://docs.python.org/3.6/library/logging.html#levels),
but case-insensitive for the sake of convenience:

```text
"critical", "error", "warning", "info", "debug", "notset"
```

### log.level_logfile

The log level used to log to the log file. Possible allowed values are the ones
defined by [Python](https://docs.python.org/3.6/library/logging.html#levels),
but case-insensitive for the sake of convenience:

```text
"critical", "error", "warning", "info", "debug", "notset"
```

### log.datefmt_console

The format string for the date/time portion of a message, when logged to the
console.

For more information on how to construct the format string please consult the
table under [Python's documentation of time.strftime(format[, t])](https://docs.python.org/3.6/library/time.html#time.strftime).

### log.datefmt_logfile

The format string for the date/time portion of a message, when logged to a log
 file.

For more information on how to construct the format string please consult the
table under [Python's documentation of time.strftime(format[, t])](https://docs.python.org/3.6/library/time.html#time.strftime).

### log.fmt_console

A string used to format the log messages when logged to the console.

For more information on possible formatting options please consult Python's
documentation on
[LogRecord attributes](https://docs.python.org/3.6/library/logging.html#logrecord-attributes).

### log.fmt_logfile

A string used to format the log messages when logged to a log file.

For more information on possible formatting options please consult Python's
documentation on
[LogRecord attributes](https://docs.python.org/3.6/library/logging.html#logrecord-attributes).

### log.granular_levels

Log levels for BigchainDB's modules. This can be useful to control the log
level of specific parts of the application. As an example, if you wanted the
logging of the `core.py` module to be more verbose, you would set the
 configuration shown in the example below.

**Example**

```js
{
    "log": {
        "granular_levels": {
            "bichaindb.core": "debug"
        }
}
```

**Default value**

```js
{}
```

## tendermint.*

The settings with names of the form `tendermint.*` tell BigchainDB Server
where it can connect to the node's Tendermint instance.

* `tendermint.host` is the hostname (FQDN)/IP address of the Tendermint instance.
* `tendermint.port` is self-explanatory.

**Example using environment variables**

```text
export BIGCHAINDB_TENDERMINT_HOST=tendermint
export BIGCHAINDB_TENDERMINT_PORT=26657
```

**Default values**

```js
"tendermint": {
    "host": "localhost",
    "port": 26657
}
```
