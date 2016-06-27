# Backing Up & Restoring Data

There are several ways to backup and restore the data in a BigchainDB cluster.

It's worth remembering that RethinkDB already has internal replication: every document is stored on _R_ different nodes, where _R_ is the replication factor (set using `bigchaindb set-replicas R`). Those replicas can be thought of as "live backups" because if one node goes down, the cluster will continue to work and no data will be lost.


## rethinkdb dump (to a File)

RethinkDB can create an archive of all data in the cluster (or all data in specified tables), as a compressed file. According to [the RethinkDB blog post when that functionality became available](https://rethinkdb.com/blog/1.7-release/):

> Since the backup process is using client drivers, it automatically takes advantage of the MVCC [multiversion concurrency control] functionality built into RethinkDB. It will use some cluster resources, but will not lock out any of the clients, so you can safely run it on a live cluster.

To back up all the data in a BigchainDB cluster, the RethinkDB admin user must run a command like the following on one of the nodes:
```text
rethinkdb dump -e bigchain.bigchain -e bigchain.votes
```

That will write a file named `rethinkdb_dump_<date>_<time>.tar.gz`. The `-e` option is used to specify which tables should be exported. You probably don't need to export the backlog table, but you definitely need to export the bigchain and votes tables. 
`bigchain.votes` means the `votes` table in the RethinkDB database named `bigchain`. It's possible that your database has a different name: [the database name is a BigchainDB configuration setting](../nodes/configuration.html#database-host-database-port-database-name). The default name is `bigchain`. (Tip: you can see the values of all configuration settings using the `bigchaindb show-config` command.)

There's [more information about the `rethinkdb dump` command in the RethinkDB documentation](https://www.rethinkdb.com/docs/backup/). It also explains how to restore data to a cluster from an archive file.

What gets backed up? The state of the database when the command was started

**Pros and Cons**

* It can take a very long time to backup data this way. The more data, the longer it will take.

* You need enough free disk space to store the backup file.

* If a document changes after the backup starts but before it ends, then the changed document may not be in the final backup. This shouldn't be a problem for BigchainDB, because blocks and votes can't change anyway.


**Notes**

* The `rethinkdb dump` subcommand saves database and table contents and metadata, but does not save cluster configuration data.

* RethinkDB also has [subcommands to import/export](https://gist.github.com/coffeemug/5894257) collections of JSON or CSV files. While one could use those for backup/restore, it wouldn't be very practical.


## Client-Side Backup

In the future, it will be possible for clients to query for the blocks containing the transactions they care about, and for the votes on those blocks. They could save a local copy of those blocks and votes.

**How could we be sure blocks and votes from a client are valid?**

All blocks and votes are signed by federation nodes. Only federation nodes can produce valid signatures because only federation nodes have the necessary private keys. A client can't produce a valid signature for a block or vote.

**Could we restore an entire BigchainDB database using client-saved blocks and votes?**

Yes, but it would be difficult to know if you've recovered every block and vote. Votes link to the block they're voting on and to the previous block, so one could detect some missing blocks. It would be difficult to know if you've recovered all the votes.


## Backup by Copying RethinkDB Data Files

It's _possible_ to back up a BigchainDB database by creating a copy of your RethinkDB data files (on all nodes, at the same time), but it's impractical. If you're curious about what's involved, see the [MongoDB documentation about "Backup by Copying Underlying Data Files"](https://docs.mongodb.com/manual/core/backups/#backup-with-file-copies).


## Incremental or Continuous Backup

RethinkDB doesn't have a built-in incremental or continuous backup capability, something like what MongoDB has. Incremental backup was mentioned briefly in RethinkDB Issue [#89](https://github.com/rethinkdb/rethinkdb/issues/89).

In principle, it's not difficult to implement incremental or continuous backup for BigchainDB, since blocks and votes never change. The tricky part is making the backup process fault-tolerant: we don't want to lose data enroute to the backup location(s).

This is a first draft; we'll have more to say here in the future.
