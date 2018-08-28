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

Manage elections to add, update, or remove a validator from the validators set. The upsert-validator subcommands implement [BEP-21](https://github.com/bigchaindb/BEPs/tree/master/21), please refer it for more details.

Election management is broken into several subcommands. Below is the command line syntax for each,

#### upsert-validator new

Create a new election which proposes a change to the validator set. An election can be used to add/update/remove a validator from the validator set.

Below is the command line syntax and the return value,

```bash
$ bigchaindb upsert-validator new E_PUBKEY E_POWER E_NODE_ID --private-key PATH_TO_YOUR_PRIVATE_KEY
[SUCCESS] Submitted proposal with id: <election_id>
```

- `E_PUBKEY`: Public key of the node to be added/updated/removed.
- `E_POWER`: The new power for the `E_PUBKEY`. NOTE, if power is set to `0` then `E_PUBKEY` will be removed from the validator set when the election concludes.
- `E_NODE_ID`: Node id of `E_PUBKEY`. The node operator of `E_PUBKEY` can generate the node id via `tendermint show_node_id`. 
- `--private-key`: The path to Tendermint's private key which can be generally found at `/home/user/.tendermint/config/priv_validator.json`. For example, to add a new validator, provide the public key and node id for some node not already in the validator set, along with whatever voting power you'd like them to have. To remove an existing validator, provide their public key and node id, and set `E_POWER` to `0`. Please note that the private key provided here is of the node which is generating this election i.e. 


NOTE: A change to the validator set can only be proposed by one of the exisitng validators.

Example usage,

```bash
$ bigchaindb upsert-validator new HHG0IQRybpT6nJMIWWFWhMczCLHt6xcm7eP52GnGuPY= 1 fb7140f03a4ffad899fabbbf655b97e0321add66 --private-key /home/user/.tendermint/config/priv_validator.json
[SUCCESS] Submitted proposal with id: 04a067582cf03eba2b53b82e4adb5ece424474cbd4f7183780855a93ac5e3caa
```

If the command succeeds, it will create an election and return an `election_id`. A successful execution of the above command **doesn't** imply that the validator set will be immediately updated but rather it means the proposal has been succcessfully accepted by the network. Once the `election_id` has been generated the node operator should share this `election_id` with other validators in the network and urge them to approve the proposal. Note that the node operator should themsleves also approve the proposal.


**NOTE**: The election proposal consists of vote tokens allocated to each current validator as per their voting power. Validators then cast their votes to approve the change to the validator set by spending their vote tokens.


#### upsert-validator approve

Approve an election by voting for it. The propsal generated by executing `bigchaindb upsert-valdiator approve ...` can approved by the validators using this command. The validator who is approving the proposal will spend all their votes i.e. if the validator has a network power of `10` then they will cast `10` votes for the proposal.`
Below is the command line syntax and the return value,

 ```bash
$ bigchaindb upsert-validator approve <election_id> --private-key PATH_TO_YOUR_PRIVATE_KEY
[SUCCESS] Your vote has been submitted
```

- `election_id` is the transaction id of the election the approval should be given for.
- `--private-key` should be the path to Tendermint's private key which can be generally found at `/home/user/.tendermint/config/priv_validator.json`.

 Example usage,
 ```bash
$ bigchaindb upsert-validator approve 04a067582cf03eba2b53b82e4adb5ece424474cbd4f7183780855a93ac5e3caa --private-key /home/user/.tendermint/config/priv_validator.json
[SUCCESS] Your vote has been submitted
```

If the command succeeds a message will be returned stating that the vote was submitted successfully. Once a proposal has been approved by sufficent validators (more than `2/3` of the total voting power) then the proposed change is applied to the network. For example, consider a network wherein the total power is `90` then the proposed changed applied only after `60` (`2/3 * 90`) have been received.
