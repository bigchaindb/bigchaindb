# Command Line Interface (CLI)

The command-line command to interact with BigchainDB Server is `bigchaindb`.


## bigchaindb \-\-help

Show help for the `bigchaindb` command. `bigchaindb -h` does the same thing.


## bigchaindb \-\-version

Show the version number. `bigchaindb -v` does the same thing.


## bigchaindb configure

Generate a local configuration file (which can be used to set some or all [BigchainDB node configuration settings](configuration.html)). It will ask you for the values of some configuration settings.
If you press Enter for a value, it will use the default value.

At this point, only one database backend is supported: `localmongodb`.

If you use the `-c` command-line option, it will generate the file at the specified path:
```text
bigchaindb -c path/to/new_config.json configure localmongodb
```

If you don't use the `-c` command-line option, the file will be written to `$HOME/.bigchaindb` (the default location where BigchainDB looks for a config file, if one isn't specified).

If you use the `-y` command-line option, then there won't be any interactive prompts: it will use the default values for all the configuration settings.
```text
bigchaindb -y configure localmongodb
```


## bigchaindb show-config

Show the values of the [BigchainDB node configuration settings](configuration.html).


## bigchaindb init

Create a backend database (local MongoDB), all database tables/collections,
various backend database indexes, and the genesis block.


## bigchaindb drop

Drop (erase) the backend database (the local MongoDB database used by this node).
You will be prompted to make sure.
If you want to force-drop the database (i.e. skipping the yes/no prompt), then use `bigchaindb -y drop`


## bigchaindb start

Start BigchainDB. It always begins by trying a `bigchaindb init` first. See the documentation for `bigchaindb init`.
The database initialization step is optional and can be skipped by passing the `--no-init` flag, i.e. `bigchaindb start --no-init`.

### Options

The log level for the console can be set via the option `--log-level` or its
abbreviation `-l`. Example:

```bash
$ bigchaindb --log-level INFO start
```

The allowed levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.
For an explanation regarding these levels please consult the
[Logging Levels](https://docs.python.org/3.6/library/logging.html#levels)
section of Python's documentation.

For a more fine-grained control over the logging configuration you can use the
configuration file as documented under
[Configuration Settings](configuration.html).


## bigchaindb upsert-validator
Add, update, or remove a validator from the validators set of the local node. The command implements [3/UPSERT-VALIDATORS](https://github.com/bigchaindb/BEPs/tree/master/3), check it out if you need more details on how this is orchestrated.

Below is the command line syntax,

```bash
$ bigchaindb upsert-validator PUBLIC_KEY_OF_VALIDATOR POWER
```

Example usage,

```bash
$ bigchaindb upsert-validator B0E42D2589A455EAD339A035D6CE1C8C3E25863F268120AA0162AD7D003A4014 10
```

If the command is returns without any error then a request to update the validator set has been successfully submitted. So, even if the command has been successfully executed it doesn't imply that the validator set has been updated. In order to check whether the change has been applied, the node operator can execute `curl http://node_ip:9985/api/v1/validators` which will list the current validators set. Refer to the [validators](/http-client-server-api.html#validators) section of the HTTP API docs for more detail.

Note:
- When `POWER`is set to `0` then the validator will be removed from the validator set.
- Upsert requests are handled once per block i.e. the validators set is updated once a new block is committed. So, the node operator is not allowed to submit a new upsert request until the current request has been processed. Furthermore, if Tendermint is started with `--consensus.create_empty_blocks=false`, and there are no new incoming transactions then the validators set update is delayed until any new transactions are received and a new block can be committed.
