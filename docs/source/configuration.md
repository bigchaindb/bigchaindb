# Configuring a BigchainDB Node

The BigchainDB configuration settings for a particular node are stored on that node in a configuration file at `$HOME/.bigchaindb`. That file doesn't exist by default. (It's not created when installing BigchainDB.) One could create it using a text editor, but it's easiest to use the `bigchaindb configure` command:

```text
$ bigchaindb configure
```

It will ask some questions and generate a new keypair (i.e. a private key and corresponding public key for the node). See below for some additional explanation of the settings and their meanings. To accept a suggested default value, press Enter or Return. If you want to accept all the default values, use the `-y` option when running the command, that is:

```text
$ bigchaindb -y configure
```

## Using a Different Path for the Configuration File

By default, the configuration settings are stored in `$HOME/.bigchaindb`. If you want to
specify a different path for your configuration file, you can use the `-c` parameter.
This works for every subcommand under the `bigchaindb` executable.

For example, if you want to **generate** a new configuration file under a
specific path, you can run:

```
$ bigchaindb -c local.json configure
$ bigchaindb -c test.json configure
```

This will create two new files named `local.json` and `test.json` in your
current working directory.

From now on, you can refer to those configuration files using the `-c`
parameter; for example:

```
$ bigchaindb -c local.json show-config
```

will show the configuration for `local.json`.

If you want to **start** BigchainDB with the `test.json` configuration file, you can use:

```
$ bigchaindb -c test.json start
```


## Using Environment Variables to Configure the Node

Sometimes it's more convenient to use environment variables to configure the
system, for example when using Docker or Heroku. In
that case you can configure the system using environment variables.

Every configuration parameter can be mapped to an environment variable. The
environment variables available are:

- `BIGCHAINDB_DATABASE_HOST` defines the RethinkDB database hostname to connect to.
- `BIGCHAINDB_DATABASE_PORT` defines the RethinkDB database port to connect to.
- `BIGCHAINDB_DATABASE_NAME` defines the RethinkDB database name to use.
- `BIGCHAINDB_KEYPAIR_PUBLIC` defines the public key of the BigchainDB node.
- `BIGCHAINDB_KEYPAIR_PRIVATE` defines the private key of the BigchainDB node.
- `BIGCHAINDB_KEYRING` is a colon-separated list of the public keys of all _other_ nodes in the cluster.
- `BIGCHAINDB_STATSD_HOST` defines the hostname of the statsd server for [monitoring](monitoring.html).
- `BIGCHAINDB_STATSD_PORT` defines the port of the statsd server for monitoring.
- `BIGCHAINDB_STATSD_RATE` is a float between `0` and `1` that defines the fraction of transaction operations sampled.
- `BIGCHAINDB_API_ENDPOINT` defines the API endpoint to use (e.g. `http://localhost:9984/api/v1`).
- `BIGCHAINDB_CONSENSUS_PLUGIN` defines the name of the [consensus plugin](consensus.html) to use.
- `BIGCHAINDB_SERVER_BIND` defines where to bind the server socket, the format is `addr:port` (e.g. `0.0.0.0:9984`).
- `BIGCHAINDB_SERVER_WORKERS` defines the [number of workers](http://docs.gunicorn.org/en/stable/settings.html#workers)
  to start for the server API.
- `BIGCHAINDB_SERVER_THREADS` defines the [number of threads](http://docs.gunicorn.org/en/stable/settings.html#threads)
  to start for the server API.


## Order of Precedence in Determining Configuration Values

All configuration values start with their default values (defined in `bigchaindb.__init__`), but a default value can be overriden by an environment variable, and a value set by an environment variable can be overriden by a value in a local configuration file (`$HOME/.bigchaindb` or the location specified by the `-c` command-line option).

In summary, there is an order of precedence in reading configuration values:
1. local configuration file
2. environment variables
3. default configuration file (defined in ``bigchaindb.__init__``)

This means that if the default configuration contains:

```json
{
    "database": {
        "host": "localhost",
        "port": 28015
    }
}
```

while the local file `local.json` contains:
```json
{
    "database": {
        "host": "ec2-xx-xx-xxx-xxx.eu-central-1.compute.amazonaws.com"
    }
}

```

and you run this command:
```
$ BIGCHAINDB_DATABASE_HOST=anotherhost.com \
  BIGCHAINDB_DATABASE_PORT=4242 \
  BIGCHAINDB_KEYRING=pubkey0:pubkey1 \
  bigchaindb -c local.json show-config
```

you will get the following values for all the configuration settings:
```json
{
    "api_endpoint": "http://localhost:8008/api/v1",
    "consensus_plugin": "default",
    "database": {
        "host": "ec2-xx-xx-xxx-xxx.eu-central-1.compute.amazonaws.com",
        "name": "bigchain",
        "port": 4242
    },
    "keypair": {
        "private": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "public": "nJq6EmdUkvFjQRB5hFvDmvZtv1deb3W3RgmiAq6dyygC"
    },
    "keyring": [
        "pubkey0",
        "pubkey1"
    ],
    "server": {
        "bind": "0.0.0.0:9984",
        "threads": null,
        "workers": null
    },
    "statsd": {
        "host": "localhost",
        "port": 8125,
        "rate": 0.01
    }
}
```


## Another Example

As another example, let's assume we **don't** have any configuration file stored in
`$HOME/.bigchaindb`. As you can see, `show-config` displays the default configuration (and a
warning):
```
$ bigchaindb show-config
WARNING:bigchaindb.config_utils:Cannot find config file `/home/vrde/.bigchaindb`.
{
    "api_endpoint": "http://localhost:9984/api/v1",
    "consensus_plugin": "default",
    "database": {
        "host": "localhost",
        "name": "bigchain",
        "port": 28015
    },
    "keypair": {
        "private": null,
        "public": null
    },
    "keyring": [],
    "server": {
        "bind": "0.0.0.0:9984",
        "threads": null,
        "workers": null
    },
    "statsd": {
        "host": "localhost",
        "port": 8125,
        "rate": 0.01
    }
}
```

If we try to run the node, the command will fail:

```
$ bigchaindb start
WARNING:bigchaindb.config_utils:Cannot find config file `/home/vrde/.bigchaindb`.
Cannot start BigchainDB, no keypair found. Did you run `bigchaindb configure`?
```

This is failing as expected: a BigchainDB node needs at least a key pair to work.
We can pass the key pair using environment variables:
```
$ BIGCHAINDB_KEYPAIR_PUBLIC=26y9EuyGP44JXxqcvF8GbCJGqkiqFXddZzxVjLU3rWbHp \
  BIGCHAINDB_KEYPAIR_PRIVATE=9PkLfHbzXnSSNnb1sSBL73C2MydzKLs5fAHoA4Q7otrG \
  bigchaindb start
```

We can also run `show-config` to see how the configuration looks:
```
$ BIGCHAINDB_KEYPAIR_PUBLIC=26y9EuyGP44JXxqcvF8GbCJGqkiqFXddZzxVjLU3rWbHp \
  BIGCHAINDB_KEYPAIR_PRIVATE=9PkLfHbzXnSSNnb1sSBL73C2MydzKLs5fAHoA4Q7otrG \
  bigchaindb show-config

WARNING:bigchaindb.config_utils:Cannot find config file `/home/vrde/.bigchaindb`.
{
    "api_endpoint": "http://localhost:9984/api/v1",
    "consensus_plugin": "default",
    "database": {
        "host": "localhost",
        "name": "bigchain",
        "port": 28015
    },
    "keypair": {
        "private": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "public": "26y9EuyGP44JXxqcvF8GbCJGqkiqFXddZzxVjLU3rWbHp"
    },
    "keyring": [],
    "server": {
        "bind": "0.0.0.0:9984",
        "threads": null,
        "workers": null
    },
    "statsd": {
        "host": "localhost",
        "port": 8125,
        "rate": 0.01
    }
}
```
