<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

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

**This is an experimental feature. Users are advised not to use it in production.**


Manage elections to add, update, or remove a validator from the validators set of the local node. The upsert-validator subcommands implement [BEP-21](https://github.com/bigchaindb/BEPs/tree/master/21). Check it out if you need more details on how this is orchestrated.

Election management is broken into several subcommands. Below is the command line syntax for each,

#### upsert-validator new

Calls a new election, proposing a change to the validator set.

Below is the command line syntax and the return value,

```bash
$ bigchaindb upsert-validator new E_PUBKEY E_POWER E_NODE_ID --private-key PATH_TO_YOUR_PRIVATE_KEY
<election_id>
```

Here, `E_PUBKEY`, `E_POWER`, and `E_NODE_ID` are the public key, proposed power, and node id of the validator being voted on. `--private-key` should be the path to wherever the private key for your validator node is stored, (*not* the private key itself.). For example, to add a new validator, provide the public key and node id for some node not already in the validator set, along with whatever voting power you'd like them to have. To remove an existing validator, provide their public key and node id, and set `E_POWER` to `0`.

Example usage,

```bash
$ bigchaindb upsert-validator new B0E42D2589A455EAD339A035D6CE1C8C3E25863F268120AA0162AD7D003A4014 1 12345 --private-key /home/user/.tendermint/config/priv_validator.json
```

If the command succeeds, it will create an election and return an `election_id`. Elections consist of one vote token per voting power, issued to the members of the validator set. Validators can cast their votes to approve the change to the validator set by spending their vote tokens. The status of the election can be monitored by providing the `election_id` to the `show` subcommand.

#### upsert-validator approve
 Approve an election by voting for it.
 Below is the command line syntax and the return value,
 ```bash
$ bigchaindb upsert-validator approve <election_id> --private-key PATH_TO_YOUR_PRIVATE_KEY
```
 Here, `<election_id>` is the transaction id of the election the approval should be given for. `--private-key` should be the path to Tendermint's private key which can be generally found at `/home/user/.tendermint/config/priv_validator.json`.

 Example usage,
 ```bash
$ bigchaindb upsert-validator approve 04a067582cf03eba2b53b82e4adb5ece424474cbd4f7183780855a93ac5e3caa --private-key /home/user/.tendermint/config/priv_validator.json
```
 If the command succeeds, a message will be returned, that the vote was submitted successfully.
