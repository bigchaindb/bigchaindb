# Backing Up & Restoring Data

There are several ways to backup and restore the data in a BigchainDB cluster.


## RethinkDB's Replication as a form of Backup

RethinkDB already has internal replication: every document is stored on _R_ different nodes, where _R_ is the replication factor (set using `bigchaindb set-replicas R`). Those replicas can be thought of as "live backups" because if one node goes down, the cluster will continue to work and no data will be lost.

At this point, there should be someone saying, "But replication isn't backup!"

It's true. Replication alone isn't enough, because something bad might happen _inside_ the database, and that could affect the replicas. For example, what if someone logged in as a RethinkDB admin and did a "drop table"? We currently plan for each node to be protected by a next-generation firewall (or something similar) to prevent such things from getting very far. For example, see [issue #240](https://github.com/bigchaindb/bigchaindb/issues/240).

Nevertheless, you should still consider having normal, "cold" backups, because bad things can still happen.


## Live Replication of RethinkDB Data Files

Each BigchainDB node stores its subset of the RethinkDB data in one directory. You could set up the node's file system so that directory lives on its own hard drive. Furthermore, you could make that hard drive part of a [RAID](https://en.wikipedia.org/wiki/RAID) array, so that a second hard drive would always have a copy of the original. If the original hard drive fails, then the second hard drive could take its place and the node would continue to function. Meanwhile, the original hard drive could be replaced.

That's just one possible way of setting up the file system so as to provide extra reliability.

Another way to get similar reliability would be to mount the RethinkDB data directory on an [Amazon EBS](https://aws.amazon.com/ebs/) volume. Each Amazon EBS volume is, "automatically replicated within its Availability Zone to protect you from component failure, offering high availability and durability."

See [the section on setting up storage for RethinkDB](../dev-and-test/setup-run-node.html#set-up-storage-for-rethinkdb-data) for more details.

As with shard replication, live file-system replication protects against many failure modes, but it doesn't protect against them all. You should still consider having normal, "cold" backups.


## rethinkdb dump (to a File)

RethinkDB can create an archive of all data in the cluster (or all data in specified tables), as a compressed file. According to [the RethinkDB blog post when that functionality became available](https://rethinkdb.com/blog/1.7-release/):

> Since the backup process is using client drivers, it automatically takes advantage of the MVCC [multiversion concurrency control] functionality built into RethinkDB. It will use some cluster resources, but will not lock out any of the clients, so you can safely run it on a live cluster.

To back up all the data in a BigchainDB cluster, the RethinkDB admin user must run a command like the following on one of the nodes:
```text
rethinkdb dump -e bigchain.bigchain -e bigchain.votes
```

That should write a file named `rethinkdb_dump_<date>_<time>.tar.gz`. The `-e` option is used to specify which tables should be exported. You probably don't need to export the backlog table, but you definitely need to export the bigchain and votes tables. 
`bigchain.votes` means the `votes` table in the RethinkDB database named `bigchain`. It's possible that your database has a different name: [the database name is a BigchainDB configuration setting](../server-reference/configuration.html#database-host-database-port-database-name). The default name is `bigchain`. (Tip: you can see the values of all configuration settings using the `bigchaindb show-config` command.)

There's [more information about the `rethinkdb dump` command in the RethinkDB documentation](https://www.rethinkdb.com/docs/backup/). It also explains how to restore data to a cluster from an archive file.

**Notes**

* If the `rethinkdb dump` subcommand fails and the last line of the Traceback says "NameError: name 'file' is not defined", then you need to update your RethinkDB Python driver; do a `pip install --upgrade rethinkdb`

* It might take a long time to backup data this way. The more data, the longer it will take.

* You need enough free disk space to store the backup file.

* If a document changes after the backup starts but before it ends, then the changed document may not be in the final backup. This shouldn't be a problem for BigchainDB, because blocks and votes can't change anyway.

* `rethinkdb dump` saves data and secondary indexes, but does *not* save cluster metadata. You will need to recreate your cluster setup yourself after you run `rethinkdb restore`.

* RethinkDB also has [subcommands to import/export](https://gist.github.com/coffeemug/5894257) collections of JSON or CSV files. While one could use those for backup/restore, it wouldn't be very practical.


## Client-Side Backup

In the future, it will be possible for clients to query for the blocks containing the transactions they care about, and for the votes on those blocks. They could save a local copy of those blocks and votes.

**How could we be sure blocks and votes from a client are valid?**

All blocks and votes are signed by federation nodes. Only federation nodes can produce valid signatures because only federation nodes have the necessary private keys. A client can't produce a valid signature for a block or vote.

**Could we restore an entire BigchainDB database using client-saved blocks and votes?**

Yes, in principle, but it would be difficult to know if you've recovered every block and vote. Votes link to the block they're voting on and to the previous block, so one could detect some missing blocks. It would be difficult to know if you've recovered all the votes.


## Backup by Copying RethinkDB Data Files

It's _possible_ to back up a BigchainDB database by creating a point-in-time copy of the RethinkDB data files (on all nodes, at roughly the same time). It's not a very practical approach to backup: the resulting set of files will be much larger (collectively) than what one would get using `rethinkdb dump`, and there are no guarantees on how consistent that data will be, especially for recently-written data.

If you're curious about what's involved, see the [MongoDB documentation about "Backup by Copying Underlying Data Files"](https://docs.mongodb.com/manual/core/backups/#backup-with-file-copies). (Yes, that's documentation for MongoDB, but the principles are the same.)

See the last subsection of this page for a better way to use this idea.


## Incremental or Continuous Backup

**Incremental backup** is where backup happens on a regular basis (e.g. daily), and each one only records the changes since the last backup.

**Continuous backup** might mean incremental backup on a very regular basis (e.g. every ten minutes), or it might mean backup of every database operation as it happens. The latter is also called transaction logging or continuous archiving.

At the time of writing, RethinkDB didn't have a built-in incremental or continuous backup capability, but the idea was raised in RethinkDB issues [#89](https://github.com/rethinkdb/rethinkdb/issues/89) and [#5890](https://github.com/rethinkdb/rethinkdb/issues/5890). On July 5, 2016, Daniel Mewes (of RethinkDB) wrote the following comment on issue #5890: "We would like to add this feature [continuous backup], but haven't started working on it yet."

To get a sense of what continuous backup might look like for RethinkDB, one can look at the continuous backup options available for MongoDB. MongoDB, the company, offers continuous backup with [Ops Manager](https://www.mongodb.com/products/ops-manager) (self-hosted) or [Cloud Manager](https://www.mongodb.com/cloud) (fully managed). Features include:

* It "continuously maintains backups, so if your MongoDB deployment experiences a failure, the most recent backup is only moments behind..."
* It "offers point-in-time backups of replica sets and cluster-wide snapshots of sharded clusters. You can restore to precisely the moment you need, quickly and safely."
* "You can rebuild entire running clusters, just from your backups."
* It enables, "fast and seamless provisioning of new dev and test environments."

The MongoDB documentation has more [details about how Ops Manager Backup works](https://docs.opsmanager.mongodb.com/current/application/#backup).

Considerations for BigchainDB:

* We'd like the cost of backup to be low. To get a sense of the cost, MongoDB Cloud Manager backup [costed $30 / GB / year prepaid](https://www.mongodb.com/blog/post/lower-mms-backup-prices-backing-mongodb-now-easier-and-more-affordable). One thousand gigabytes backed up (i.e. about a terabyte) would cost 30 thousand US dollars per year. (That's just for the backup; there's also a cost per server per year.)
* We'd like the backup to be decentralized, with no single point of control or single point of failure. (Note: some file systems have a single point of failure. For example, HDFS has one Namenode.)
* We only care to back up blocks and votes, and once written, those never change. There are no updates or deletes, just new blocks and votes.


## Combining RethinkDB Replication with Storage Snapshots

Although it's not advertised as such, RethinkDB's built-in replication feature is similar to continous backup, except the "backup" (i.e. the set of replica shards) is spread across all the nodes. One could take that idea a bit farther by creating a set of backup-only servers with one full backup:

* Give all the original BigchainDB nodes (RethinkDB nodes) the server tag `original`. This is the default if you used the RethinkDB config file suggested in the section titled [Configure RethinkDB Server](../dev-and-test/setup-run-node.html#configure-rethinkdb-server).
* Set up a group of servers running RethinkDB only, and give them the server tag `backup`. The `backup` servers could be geographically separated from all the `original` nodes (or not; it's up to the federation).
* Clients shouldn't be able to read from or write to servers in the `backup` set.
* Send a RethinkDB reconfigure command to the RethinkDB cluster to make it so that the `original` set has the same number of replicas as before (or maybe one less), and the `backup` set has one replica. Also, make sure the `primary_replica_tag='original'` so that all primary shards live on the `original` nodes.

The [RethinkDB documentation on sharding and replication](https://www.rethinkdb.com/docs/sharding-and-replication/) has the details of how to set server tags and do RethinkDB reconfiguration.

Once you've set up a set of backup-only RethinkDB servers, you could make a point-in-time snapshot of their storage devices, as a form of backup.

You might want to disconnect the `backup` set from the `original` set first, and then wait for reads and writes in the `backup` set to stop. (The `backup` set should have only one copy of each shard, so there's no opportunity for inconsistency between shards of the `backup` set.)

You will want to re-connect the `backup` set to the `original` set as soon as possible, so it's able to catch up.

If something bad happens to the entire original BigchainDB cluster (including the `backup` set) and you need to restore it from a snapshot, you can, but before you make BigchainDB live, you should 1) delete all entries in the backlog table, 2) delete all blocks after the last voted-valid block, 3) delete all votes on the blocks deleted in part 2, and 4) rebuild the RethinkDB indexes.

**NOTE:** Sometimes snapshots are _incremental_. For example, [Amazon EBS snapshots](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html) are incremental, meaning "only the blocks on the device that have changed after your most recent snapshot are saved. **This minimizes the time required to create the snapshot and saves on storage costs.**" [Emphasis added]
