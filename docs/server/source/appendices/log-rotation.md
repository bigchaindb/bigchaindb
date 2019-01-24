<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Logging and Log Rotation

Each BigchainDB node runs:

- MongoDB
- BigchainDB Server
- Tendermint

When running a BigchainDB node for long periods
of time, we need to consider doing log rotation, i.e. we do not want the logs taking
up large amounts of storage and making the node unresponsive or getting it into a bad state.

## MongoDB Logging and Log Rotation

See the MongoDB docs about
[logging](https://docs.mongodb.com/v3.6/administration/monitoring/#monitoring-standard-loggging)
and [log rotation](https://docs.mongodb.com/v3.6/tutorial/rotate-log-files/).

## BigchainDB Server Logging and Log Rotation

BigchainDB Server writes its logs to two files: normal logs and error logs. The names of those files, and their locations, are set as part of the BigchainDB configuration settings. The default names and locations are:

- `~/bigchaindb.log`
- `~/bigchaindb-errors.log`

Log rotation is baked into BigchainDB Server using Python's `logging` module. The logs for BigchainDB Server are rotated when any of the above mentioned files exceeds 209715200 bytes (i.e. approximately 209 MB).

For more information, see the docs about [the BigchainDB Server configuration settings related to logging](../server-reference/configuration#log).

## Tendermint Logging and Log Rotation

Tendermint writes its logs to the files:

- `tendermint.out.log`
- `tendermint.err.log`

If you started BigchainDB Server and Tendermint using Monit, as suggested by our guide on
[How to Set Up a BigchainDB Network](../simple-deployment-template/network-setup),
then the logs will be written to `$HOME/.bigchaindb-monit/logs/`.

Moreover, if you started BigchainDB Server and Tendermint using Monit,
then Monit monitors the Tendermint log files.
Tendermint logs are rotated if any of the above mentioned log files exceeds 200 MB.
