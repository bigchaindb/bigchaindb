# Command Line Interface (CLI)

The command-line command to interact with BigchainDB Server is `bigchaindb`.


## bigchaindb \-\-help

Show help for the `bigchaindb` command. `bigchaindb -h` does the same thing.


## bigchaindb \-\-version

Show the version number. `bigchaindb -v` does the same thing.


## bigchaindb configure

Generate a local configuration file (which can be used to set some or all [BigchainDB node configuration settings](configuration.html)). It will auto-generate a public-private keypair and then ask you for the values of other configuration settings. If you press Enter for a value, it will use the default value.

Since BigchainDB supports multiple databases you need to always specify the
database backend that you want to use. At this point only two database backends
are supported: `rethinkdb` and `mongodb`.

If you use the `-c` command-line option, it will generate the file at the specified path:
```text
bigchaindb -c path/to/new_config.json configure rethinkdb
```

If you don't use the `-c` command-line option, the file will be written to `$HOME/.bigchaindb` (the default location where BigchainDB looks for a config file, if one isn't specified).

If you use the `-y` command-line option, then there won't be any interactive prompts: it will just generate a keypair and use the default values for all the other configuration settings.
```text
bigchaindb -y configure rethinkdb
```


## bigchaindb show-config

Show the values of the [BigchainDB node configuration settings](configuration.html).


## bigchaindb export-my-pubkey

Write the node's public key (i.e. one of its configuration values) to standard output (stdout).


## bigchaindb init

Create a backend database (RethinkDB or MongoDB),
all database tables/collections,
various backend database indexes,
and the genesis block.

Note: The `bigchaindb start` command (see below) always starts by trying a `bigchaindb init` first. If it sees that the backend database already exists, then it doesn't re-initialize the database. One doesn't have to do `bigchaindb init` before `bigchaindb start`. `bigchaindb init` is useful if you only want to initialize (but not start).


## bigchaindb drop

Drop (erase) the backend database (a RethinkDB or MongoDB database).
You will be prompted to make sure.
If you want to force-drop the database (i.e. skipping the yes/no prompt), then use `bigchaindb -y drop`


## bigchaindb start

Start BigchainDB. It always begins by trying a `bigchaindb init` first. See the note in the documentation for `bigchaindb init`.
You can also use the `--dev-start-rethinkdb` command line option to automatically start rethinkdb with bigchaindb if rethinkdb is not already running,
e.g. `bigchaindb --dev-start-rethinkdb start`. Note that this will also shutdown rethinkdb when the bigchaindb process stops.
The option `--dev-allow-temp-keypair` will generate a keypair on the fly if no keypair is found, this is useful when you want to run a temporary instance of BigchainDB in a Docker container, for example.

### Options
The log level for the console can be set via the option `--log-level` or its
abbreviation `-l`. Example:

```bash
$ bigchaindb --log-level INFO start
```

The allowed levels are `DEBUG`, `INFO` , `WARNING`, `ERROR`, and `CRITICAL`.
For an explanation regarding these levels please consult the 
[Logging Levels](https://docs.python.org/3.6/library/logging.html#levels)
section of Python's documentation.

For a more fine-grained control over the logging configuration you can use the
configuration file as documented under
[Configuration Settings](configuration.html).

## bigchaindb set-shards

This command is specific to RethinkDB so it will only run if BigchainDB is
configured with `rethinkdb` as the backend.

If RethinkDB is the backend database, then:
```text
$ bigchaindb set-shards 4
```

will set the number of shards (in all RethinkDB tables) to 4.


## bigchaindb set-replicas

This command is specific to RethinkDB so it will only run if BigchainDB is
configured with `rethinkdb` as the backend.

If RethinkDB is the backend database, then:
```text
$ bigchaindb set-replicas 3
```

will set the number of replicas (of each shard) to 3
(i.e. it will set the replication factor to 3).


## bigchaindb add-replicas

This command is specific to MongoDB so it will only run if BigchainDB is
configured with `mongodb` as the backend.

This command is used to add nodes to a BigchainDB cluster. It accepts a list of
space separated hosts in the form _hostname:port_:
```text
$ bigchaindb add-replicas server1.com:27017 server2.com:27017 server3.com:27017
```

## bigchaindb remove-replicas

This command is specific to MongoDB so it will only run if BigchainDB is
configured with `mongodb` as the backend.

This command is used to remove nodes from a BigchainDB cluster. It accepts a
list of space separated hosts in the form _hostname:port_:
```text
$ bigchaindb remove-replicas server1.com:27017 server2.com:27017 server3.com:27017
```
