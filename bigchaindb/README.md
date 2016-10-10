# Overview

A high-level description of the files and subdirectories of BigchainDB. Heavily used external dependencies include [`multipipes`](https://github.com/bigchaindb/multipipes) and [`bigchaindb-common`](https://github.com/bigchaindb/bigchaindb-common).

There are three database tables which underpin BigchainDB: `backlog`, where incoming transactions are held temporarily until they can be consumed by; `bigchain`, where blocks of transactions are written permanently; and `votes`, where votes are written permanently.  It is the votes in the `votes` table which must be queried to determine block validity and order. For more in-depth explanation, see [the whitepaper](https://www.bigchaindb.com/whitepaper/).

## Files

### [`core.py`](./core.py)

The `Bigchain` class is defined here.  Most operations outlined in the [whitepaper](https://www.bigchaindb.com/whitepaper/) as well as database interactions are found in this file.  This is the place to start if you are interested in implementing a server API, since many of these class methods concern BigchainDB interacting with the outside world.

### [`models.py`](./models.py)

`Block`, `Transaction`, and `Asset` classes are defined here.  The classes mirror the block and transaction structure from the [documentation](https://docs.bigchaindb.com/projects/server/en/latest/topic-guides/models.html), but also include methods for validation and signing.

### [`consensus.py`](./config_utils.py)

Base class for consensus methods (verification of votes, blocks, and transactions).  The actual logic is mostly found in `transaction` and `block` models, defined in [`models.py`](https://github.com/bigchaindb/bigchaindb/blob/master/bigchaindb/models.py).

### [`processes.py`](./processes.py)

Entry point for the BigchainDB process, after initialization.  All subprocesses are started here: processes to handle new blocks, votes, etc.

### [`config_utils.py`](./config_utils.py)

Methods for managing the configuration, including loading configuration files, automatically generating the configuration, and keeping the configuration consistent across BigchainDB instances.

### [`monitor.py`](./monitor.py)

Code for monitoring speed of various processes in BigchainDB via `statsd` and Grafana.  [See documentation.](https://docs.bigchaindb.com/projects/server/en/latest/clusters-feds/monitoring.html)

## Folders

### [`pipelines`](./pipelines)

Structure and implementation of various subprocesses started in [`processes.py`](https://github.com/bigchaindb/bigchaindb/blob/master/bigchaindb/processes.py).

### [`commands`](./commands)

Contains code for the [CLI](https://docs.bigchaindb.com/projects/server/en/latest/server-reference/bigchaindb-cli.html) for BigchainDB.

### [`db`](./db)

Code for building the database connection, creating indexes, and other database setup tasks.
