# The BigchainDB Command Line Interface (CLI)

The command-line command to interact with BigchainDB is `bigchaindb`.


## bigchaindb \-\-help

Show help for the `bigchaindb` command. `bigchaindb -h` does the same thing.


## bigchaindb configure

Generate a local config file (which can be used to set some or all [BigchainDB node configuration settings](configuration.html)). It will auto-generate a public-private keypair and then ask you for the values of other configuration settings. If you press Enter for a value, it will use the default value.

If you use the `-c` command-line option, it will generate the file at the specified path:
```text
bigchaindb -c path/to/new_config.json configure
```

If you don't use the `-c` command-line option, the file will be written to `$HOME/.bigchaindb` (the default location where BigchainDB looks for a config file, if one isn't specified).

If you use the `-y` command-line option, then there won't be any interactive prompts: it will just generate a keypair and use the default values for all the other configuration settings.
```text
bigchaindb -y configure
```


## bigchaindb show-config

Show the values of the [BigchainDB node configuration settings](configuration.html).


## bigchaindb export-my-pubkey

Write the node's public key (i.e. one of its configuration values) to standard output (stdout).


## bigchaindb init

Create a RethinkDB database, all RethinkDB database tables, various RethinkDB database indexes, and the genesis block.

Note: The `bigchaindb start` command (see below) always starts by trying a `bigchaindb init` first. If it sees that the RethinkDB database already exists, then it doesn't re-initialize the database. One doesn't have to do `bigchaindb init` before `bigchaindb start`. `bigchaindb init` is useful if you only want to initialize (but not start).


## bigchaindb drop

Drop (erase) the RethinkDB database. You will be prompted to make sure. If you want to force-drop the database (i.e. skipping the yes/no prompt), then use `bigchaindb -y drop`


## bigchaindb start

Start BigchainDB. It always begins by trying a `bigchaindb init` first. See the note in the documentation for `bigchaindb init`.


## bigchaindb load

Write transactions to the backlog (for benchmarking tests). You can learn more about it using:
```text
$ bigchaindb load -h
```

## bigchaindb set-shards

Set the number of shards in the underlying datastore. For example, the following command will set the number of shards to four:
```text
$ bigchaindb set-shards 4
```

## bigchaindb set-replicas

Set the number of replicas (of each shard) in the underlying datastore. For example, the following command will set the number of replicas to three (i.e. it will set the replication factor to three):
```text
$ bigchaindb set-replicas 3
```
