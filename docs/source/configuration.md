# Configuring a BigchainDB Node

The standard way to configure a BigchainDB node is to run the command `configure`:

```text
$ bigchaindb configure
```

This command will generate a new keypair and will guide you through the
configuration of the system. By default keypair and settings will be saved in the
`$HOME/.bigchaindb` file.


## Using a different path for the configuration

By default the configuration is stored in `$HOME/.bigchaindb`, if you want to
specify a different path for your configuration you can use the `-c` parameter.
This works for every subcommand under the `bigchaindb` executable.

For example, if you want to **generate** a new configuration file under a
specific path, you can run:

```
$ bigchaindb -c local.json configure
$ bigchaindb -c test.json configure
```

This will create two new files called `local.json` and `test.json` in your
current working directory.

From now on, you can refer to those configuration files using the `-c`
parameter, for example:

```
$ bigchaindb -c local.json show-config
```

Will show the configuration for `local.json`.

If you want to **start** BigchainDB with the `test.json` configuration, you can
try:

```
$ bigchaindb -c test.json start
```


## Using environ variables to configure the node

Sometimes it's more convenient to use environment variables to configure the
system, for example when using Docker or Heroku. Another use case is to have a
*volatile*, throw away configuration you need to test something quickly. In
those cases you can configure the system using environment variables.

Every configuration key can be mapped to an environment variable. The
environment variables available are:
```
- BIGCHAINDB_DATABASE_HOST
- BIGCHAINDB_DATABASE_PORT
- BIGCHAINDB_DATABASE_NAME
- BIGCHAINDB_KEYPAIR_PUBLIC
- BIGCHAINDB_KEYPAIR_PRIVATE
- BIGCHAINDB_KEYRING
- BIGCHAINDB_STATSD_HOST
- BIGCHAINDB_STATSD_PORT
- BIGCHAINDB_STATSD_RATE
- BIGCHAINDB_API_ENDPOINT
- BIGCHAINDB_CONSENSUS_PLUGIN
- BIGCHAINDB_SERVER_BIND
- BIGCHAINDB_SERVER_WORKERS
- BIGCHAINDB_SERVER_THREADS
```

As an example, let's assume we **don't** have any configuration file stored in
the default location `$HOME/.bigchaindb`.

As you can see, `show-config` displays the default configuration (and a
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

We can also run `show-config` to see how the configuration looks like:
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


# Precedence in reading configuration values

Note that there is a precedence in reading configuration values:
 - local config file;
 - environment vars;
 - default config file (contained in ``bigchaindb.__init__``).

This means that if the default configuration contains an entry that is:

```json
{

    "database": {
        "host": "localhost",
        "port": 28015
    }

}
```

while your local file `local.json` contains:
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

you will get:
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

Note that the type of `keyring` is a list. If you want to pass a list as an
environ variable you need to use colon (`:`) as separator.

