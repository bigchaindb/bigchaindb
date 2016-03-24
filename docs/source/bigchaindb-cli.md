# The BigchainDB Command Line Interfaces (CLIs)

BigchainDB has some Command Line Interfaces (CLIs). One of them is the `bigchaindb` command which we already saw when we first started BigchainDB using:
```text
$ bigchaindb configure
$ bigchaindb start
```

When you run `bigchaindb configure`, it creates a default configuration file in `$HOME/.bigchaindb`. You can check that configuration using:
```text
$ bigchaindb show-config
```

To find out what else you can do with the `bigchain` command, use:
```text
$ bigchaindb -h
```

There's another command named `bigchaindb-benchmark`. It's used to run benchmarking tests. You can learn more about it using:
```text
$ bigchaindb-benchmark -h
$ bigchaindb-benchmark load -h
```

Note that you can always start `bigchaindb` using a different config file using the `-c` option.
For more information check the help with `bigchaindb -h`.


# Precedence in reading configuration values

Note that there is a precedence in reading configuration values:
 - (**not yet**) command line;
 - local config file;
 - environment vars;
 - default config file (contained in ``bigchaindb.__init__``).

This means that if the default configuration contains an entry that is:

```
{...
    "database": {"host": "localhost",
                 "port": 28015}
...}
```

while your local file `local.json` contains:
```
{...
    "database": {"host": "whatever"}
...}
```

and you run this command:
```
$ BIGCHAINDB_DATABASE_HOST=foobar BIGCHAINDB_DATABASE_PORT=42000 bigchaindb -c local.json show-config
```

you will get:
```
INFO:bigchaindb.config_utils:Configuration loaded from `local.json`
{'CONFIGURED': True,
 'api_endpoint': 'http://localhost:8008/api/v1',
 'consensus_plugin': 'default',
 'database': {'host': 'localhost', 'name': 'bigchain', 'port': 28015},
 'keypair': {'private': 'Hbqvh...',
             'public': '2Bi5NU...'},
 'keyring': [],
 'statsd': {'host': 'localhost', 'port': 8125, 'rate': 0.01}}

```

# List of env variables

```
- BIGCHAINDB_DATABASE_HOST
- BIGCHAINDB_DATABASE_PORT
- BIGCHAINDB_DATABASE_NAME
- BIGCHAINDB_KEYPAIR_PUBLIC
- BIGCHAINDB_KEYPAIR_PRIVATE
- BIGCHAINDB_STATSD_HOST
- BIGCHAINDB_STATSD_PORT
- BIGCHAINDB_STATSD_RATE
- BIGCHAINDB_API_ENDPOINT
- BIGCHAINDB_CONSENSUS_PLUGIN
```
