<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Log rotation for a BigchainDB node

Each BigchainDB node comprises of 3 main services:
  - BigchainDB server
  - Tendermint
  - MongoDB

To run a BigchainDB test network/dev node, that is expected to run for relatively longer periods
of time, we need to consider the log rotation of these services i.e. we do not want the logs taking
up large amounts of storage and making the node unresponsive or get into bad state.

## Log rotation for MongoDB

Currently, we leave the log rotation of MongoDB to the BigchainDB administrator. For more notes on MongoDB log rotation
please refer to [MongoDB docs](https://docs.mongodb.com/v3.6/tutorial/rotate-log-files/).

## Log rotation for BigchainDB

Log rotation is baked into BigchainDB server using the `logging` module. BigchainDB server logs information into the following files:
 - `bigchaindb.log`
 - `bigchaindb-errors.log`

These log files are created by default in the directory from where you run `bigchaindb start`, if you are using `monit`, from 
[How to Set Up a BigchainDB Network](../simple-deployment-template/network-setup.md) guide, the default directory is: `$HOME/.bigchaindb-monit/logs`

The logs for BigchainDB server are rotated when any of the above mentioned file exceeds `209715200 bytes (i.e. approximately 209 MB).`.


## Log rotation for Tendermint

In order to set up log rotation of Tendermint, you will need to use the [Monit]( https://www.mmonit.com/monit) scripts provided by us. Covered in the [How to Set Up a BigchainDB Network](../simple-deployment-template/network-setup.md) guide.

```bash
$ monit -d 1
```

Monit monitors both Tendermint and BigchainDB processes as well as the Tendermint log files, `tendermint.out.log` and `tendermint.err.log`. Default location for these log files is:
`$HOME/.bigchaindb-monit/logs`.

Tendermint logs are rotated if any of the above mentioned log files exceeds `200 MB` in size.

