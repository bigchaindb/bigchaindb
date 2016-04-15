# The BigchainDB Command Line Interface (CLI)

There are some command-line commands for working with BigchainDB: `bigchaindb` and `bigchaindb-benchmark`. This section provides an overview of those commands.

## bigchaindb

### bigchaindb --help

One can get basic help with the `bigchaindb` command using `bigchaindb --help` or `bigchaindb -h`.

### bigchaindb configure

This command generates a public/private keypair for the node, and writes a BigchainDB configuration file to the node's file system. It's documented in the section [Configuring a BigchainDB Node](configuration.html).

If you want to force-generate a new configuration file regardless of whether one already exists (i.e. skipping the yes/no prompt), then use `bigchaindb -y configure`.

### bigchaindb add-to-keyring KEY

This command is used to add a single public key (KEY) to the node's keyring (a list of public keys of _other_ nodes in the federation). For example, this command:
```text
bigchaindb add-to-keyring F9C2vsnEkiaeUTrDRnJrmtV1AJxWjud9eTvMU5LLqa1C
```

adds the public key `F9C2vsnEkiaeUTrDRnJrmtV1AJxWjud9eTvMU5LLqa1C` to the node's keyring. If you attempt to add the node's own public key, or you attempt to add a key that's already in the keyring, then no key will be added to the keyring.

### bigchaindb show-config

This command shows the values of the configuration settings, which can come from a variety of sources. See [the section on configuring BigchainDB](configuration.html) for more details and examples.

### bigchaindb export-my-pubkey

This command writes the node's public key (i.e. one of its configuration values) to standard output (stdout).

### bigchaindb init

This command creates a RethinkDB database, two RethinkDB database tables (backlog and bigchain), various RethinkDB database indexes, and the genesis block.

Note: The `bigchaindb start` command (see below) always starts by trying a `bigchaindb init` first. If it sees that the RethinkDB database already exists, then it doesn't re-initialize the database. One doesn't have to do `bigchaindb init` before `bigchaindb start`. `bigchaindb init` is useful if you only want to initialize (but not start).

### bigchaindb drop

This command drops (erases) the RethinkDB database. You will be prompted to make sure. If you want to force-drop the database (i.e. skipping the yes/no prompt), then use `bigchaindb -y drop`

### bigchaindb start

This command starts BigchainDB. It always begins by trying a `bigchaindb init` first. See the note in the documentation for `bigchaindb init`.


## bigchaindb-benchmark

The `bigchaindb-benchmark` command is used to run benchmarking tests. You can learn more about it using:
```text
$ bigchaindb-benchmark -h
$ bigchaindb-benchmark load -h
```
