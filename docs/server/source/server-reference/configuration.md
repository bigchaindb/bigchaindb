# Configuration Settings

The value of each BigchainDB Server configuration setting is determined according to the following rules:

* If it's set by an environment variable, then use that value
* Otherwise, if it's set in a local config file, then use that value
* Otherwise, use the default value

For convenience, here's a list of all the relevant environment variables (documented below):

`BIGCHAINDB_DATABASE_BACKEND`<br>
`BIGCHAINDB_DATABASE_HOST`<br>
`BIGCHAINDB_DATABASE_PORT`<br>
`BIGCHAINDB_DATABASE_NAME`<br>
`BIGCHAINDB_DATABASE_CONNECTION_TIMEOUT`<br>
`BIGCHAINDB_DATABASE_MAX_TRIES`<br>
`BIGCHAINDB_SERVER_BIND`<br>
`BIGCHAINDB_SERVER_LOGLEVEL`<br>
`BIGCHAINDB_SERVER_WORKERS`<br>
`BIGCHAINDB_WSSERVER_SCHEME`<br>
`BIGCHAINDB_WSSERVER_HOST`<br>
`BIGCHAINDB_WSSERVER_PORT`<br>
`BIGCHAINDB_WSSERVER_ADVERTISED_SCHEME`<br>
`BIGCHAINDB_WSSERVER_ADVERTISED_HOST`<br>
`BIGCHAINDB_WSSERVER_ADVERTISED_PORT`<br>
`BIGCHAINDB_CONFIG_PATH`<br>
`BIGCHAINDB_LOG`<br>
`BIGCHAINDB_LOG_FILE`<br>
`BIGCHAINDB_LOG_ERROR_FILE`<br>
`BIGCHAINDB_LOG_LEVEL_CONSOLE`<br>
`BIGCHAINDB_LOG_LEVEL_LOGFILE`<br>
`BIGCHAINDB_LOG_DATEFMT_CONSOLE`<br>
`BIGCHAINDB_LOG_DATEFMT_LOGFILE`<br>
`BIGCHAINDB_LOG_FMT_CONSOLE`<br>
`BIGCHAINDB_LOG_FMT_LOGFILE`<br>


The local config file is `$HOME/.bigchaindb` by default (a file which might not even exist), but you can tell BigchainDB to use a different file by using the `-c` command-line option, e.g. `bigchaindb -c path/to/config_file.json start`
or using the `BIGCHAINDB_CONFIG_PATH` environment variable, e.g. `BIGHAINDB_CONFIG_PATH=.my_bigchaindb_config bigchaindb start`.
Note that the `-c` command line option will always take precedence if both the `BIGCHAINDB_CONFIG_PATH` and the `-c` command line option are used.

You can read the current default values in the file [bigchaindb/\_\_init\_\_.py](https://github.com/bigchaindb/bigchaindb/blob/master/bigchaindb/__init__.py). (The link is to the latest version.)

Running `bigchaindb -y configure localmongodb` will generate a local config file in `$HOME/.bigchaindb` with all the default values.



## database.*

The settings with names of the form `database.*` are for the database backend
(currently only MongoDB). They are:

* `database.backend` is only `localmongodb`, currently.
* `database.host` is the hostname (FQDN) of the backend database.
* `database.port` is self-explanatory.
* `database.name` is a user-chosen name for the database inside MongoDB, e.g. `bigchain`.
* `database.connection_timeout` is the maximum number of milliseconds that BigchainDB will wait before giving up on one attempt to connect to the database backend.
* `database.max_tries` is the maximum number of times that BigchainDB will try to establish a connection with the database backend. If 0, then it will try forever.

**Example using environment variables**
```text
export BIGCHAINDB_DATABASE_BACKEND=localmongodb
export BIGCHAINDB_DATABASE_HOST=localhost
export BIGCHAINDB_DATABASE_PORT=27017
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
    "replicaset": null,
    "connection_timeout": 5000,
    "max_tries": 3,
    "login": null,
    "password": null
    "ssl": false,
    "ca_cert": null,
    "crlfile": null,
    "certfile": null,
    "keyfile": null,
    "keyfile_passphrase": null,
}
```


## server.bind, server.loglevel & server.workers

These settings are for the [Gunicorn HTTP server](http://gunicorn.org/), which is used to serve the [HTTP client-server API](../http-client-server-api.html).

`server.bind` is where to bind the Gunicorn HTTP server socket. It's a string. It can be any valid value for [Gunicorn's bind setting](http://docs.gunicorn.org/en/stable/settings.html#bind). If you want to allow IPv4 connections from anyone, on port 9984, use `0.0.0.0:9984`. In a production setting, we recommend you use Gunicorn behind a reverse proxy server. If Gunicorn and the reverse proxy are running on the same machine, then use `localhost:PORT` where PORT is _not_ 9984 (because the reverse proxy needs to listen on port 9984). Maybe use PORT=9983 in that case because we know 9983 isn't used. If Gunicorn and the reverse proxy are running on different machines, then use `A.B.C.D:9984` where A.B.C.D is the IP address of the reverse proxy. There's [more information about deploying behind a reverse proxy in the Gunicorn documentation](http://docs.gunicorn.org/en/stable/deploy.html). (They call it a proxy.)

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


## wsserver.scheme, wsserver.host and wsserver.port

These settings are for the
[aiohttp server](https://aiohttp.readthedocs.io/en/stable/index.html),
which is used to serve the
[WebSocket Event Stream API](../websocket-event-stream-api.html).
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

## wsserver.advertised_scheme, wsserver.advertised_host and wsserver.advertised_port

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

## log

The `log` key is expected to point to a mapping (set of key/value pairs)
holding the logging configuration.

**Example**:

```
{
    "log": {
        "file": "/var/log/bigchaindb.log",
        "error_file": "/var/log/bigchaindb-errors.log",
        "level_console": "info",
        "level_logfile": "info",
        "datefmt_console": "%Y-%m-%d %H:%M:%S",
        "datefmt_logfile": "%Y-%m-%d %H:%M:%S",
        "fmt_console": "%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
        "fmt_logfile": "%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
}
```

**Defaults to**:

```
{
    "log": {
        "file": "~/bigchaindb.log",
        "error_file": "~/bigchaindb-errors.log",
        "level_console": "info",
        "level_logfile": "info",
        "datefmt_console": "%Y-%m-%d %H:%M:%S",
        "datefmt_logfile": "%Y-%m-%d %H:%M:%S",
        "fmt_logfile": "[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s (%(processName)-10s - pid: %(process)d)",
        "fmt_console": "[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s (%(processName)-10s - pid: %(process)d)"
}
```

The next subsections explain each field of the `log` configuration.


### log.file & log.error_file
The full paths to the files where logs and error logs should be written to.

**Example**:

```
{
    "log": {
        "file": "/var/log/bigchaindb/bigchaindb.log"
        "error_file": "/var/log/bigchaindb/bigchaindb-errors.log"
    }
}
```

**Defaults to**:

    * `"~/bigchaindb.log"`
    * `"~/bigchaindb-errors.log"`

Please note that the user running `bigchaindb` must have write access to the
locations.

#### Log rotation

Log files have a size limit of 200 MB and will be rotated up to five times.

For example if we consider the log file setting:

```
{
    "log": {
        "file": "~/bigchain.log"
    }
}
```

logs would always be written to `bigchain.log`. Each time the file
`bigchain.log` reaches 200 MB it would be closed and renamed
`bigchain.log.1`. If `bigchain.log.1` and `bigchain.log.2` already exist they
would be renamed `bigchain.log.2` and `bigchain.log.3`. This pattern would be
applied up to `bigchain.log.5` after which `bigchain.log.5` would be
overwritten by `bigchain.log.4`, thus ending the rotation cycle of whatever
logs were in `bigchain.log.5`.


### log.level_console
The log level used to log to the console. Possible allowed values are the ones
defined by [Python](https://docs.python.org/3.6/library/logging.html#levels),
but case insensitive for convenience's sake:

```
"critical", "error", "warning", "info", "debug", "notset"
```

**Example**:

```
{
    "log": {
        "level_console": "info"
    }
}
```

**Defaults to**: `"info"`.


### log.level_logfile
The log level used to log to the log file. Possible allowed values are the ones
defined by [Python](https://docs.python.org/3.6/library/logging.html#levels),
but case insensitive for convenience's sake:

```
"critical", "error", "warning", "info", "debug", "notset"
```

**Example**:

```
{
    "log": {
        "level_file": "info"
    }
}
```

**Defaults to**: `"info"`.


### log.datefmt_console
The format string for the date/time portion of a message, when logged to the
console.

**Example**:

```
{
    "log": {
        "datefmt_console": "%x %X %Z"
    }
}
```

**Defaults to**: `"%Y-%m-%d %H:%M:%S"`.

For more information on how to construct the format string please consult the
table under Python's documentation of
 [`time.strftime(format[, t])`](https://docs.python.org/3.6/library/time.html#time.strftime)

### log.datefmt_logfile
The format string for the date/time portion of a message, when logged to a log
 file.

**Example**:

```
{
    "log": {
        "datefmt_logfile": "%c %z"
    }
}
```

**Defaults to**: `"%Y-%m-%d %H:%M:%S"`.

For more information on how to construct the format string please consult the
table under Python's documentation of
 [`time.strftime(format[, t])`](https://docs.python.org/3.6/library/time.html#time.strftime)


### log.fmt_console
A string used to format the log messages when logged to the console.

**Example**:

```
{
    "log": {
        "fmt_console": "%(asctime)s [%(levelname)s] %(message)s %(process)d"
    }
}
```

**Defaults to**: `"[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s (%(processName)-10s - pid: %(process)d)"`

For more information on possible formatting options please consult Python's
documentation on
[LogRecord attributes](https://docs.python.org/3.6/library/logging.html#logrecord-attributes)


### log.fmt_logfile
A string used to format the log messages when logged to a log file.

**Example**:

```
{
    "log": {
        "fmt_logfile": "%(asctime)s [%(levelname)s] %(message)s %(process)d"
    }
}
```

**Defaults to**: `"[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s (%(processName)-10s - pid: %(process)d)"`

For more information on possible formatting options please consult Python's
documentation on
[LogRecord attributes](https://docs.python.org/3.6/library/logging.html#logrecord-attributes)


### log.granular_levels
Log levels for BigchainDB's modules. This can be useful to control the log
level of specific parts of the application. As an example, if you wanted the
logging of the `core.py` module to be more verbose, you would set the
 configuration shown in the example below.

**Example**:

```
{
    "log": {
        "granular_levels": {
            "bichaindb.core": "debug"
        }
}
```

**Defaults to**: `{}`
