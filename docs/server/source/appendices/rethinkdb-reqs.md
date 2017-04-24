# RethinkDB Requirements

[The RethinkDB documentation](https://rethinkdb.com/docs/) should be your first source of information about its requirements. This page serves mostly to document some of its more obscure requirements.

RethinkDB Server [will run on any modern OS](https://www.rethinkdb.com/docs/install/). Note that the Fedora package isn't officially supported. Also, official support for Windows is fairly recent ([April 2016](https://rethinkdb.com/blog/2.3-release/)).


## Storage Requirements

When it comes to storage for RethinkDB, there are many things that are nice to have (e.g. SSDs, high-speed input/output [IOPS], replication, reliability, scalability, pay-for-what-you-use), but there are few _requirements_ other than:

1. have enough storage to store all your data (and its replicas), and
2. make sure your storage solution (hardware and interconnects) can handle your expected read & write rates.

For RethinkDB's failover mechanisms to work, [every RethinkDB table must have at least three replicas](https://rethinkdb.com/docs/failover/) (i.e. a primary replica and two others). For example, if you want to store 10 GB of unique data, then you need at least 30 GB of storage. (Indexes and internal metadata are stored in RAM.)

As for the read & write rates, what do you expect those to be for your situation? It's not enough for the storage system alone to handle those rates: the interconnects between the nodes must also be able to handle them.

**Storage Notes Specific to RethinkDB**

* The RethinkDB storage engine has a number of SSD optimizations, so you _can_ benefit from using SSDs. ([source](https://www.rethinkdb.com/docs/architecture/))

* If you have an N-node RethinkDB cluster and 1) you want to use it to store an amount of data D (unique records, before replication), 2) you want the replication factor to be R (all tables), and 3) you want N shards (all tables), then each BigchainDB node must have storage space of at least R×D/N.

* RethinkDB tables can have [at most 64 shards](https://rethinkdb.com/limitations/). What does that imply? Suppose you only have one table, with 64 shards. How big could that table be? It depends on how much data can be stored in each node. If the maximum amount of data that a node can store is d, then the biggest-possible shard is d, and the biggest-possible table size is 64 times that. (All shard replicas would have to be stored on other nodes beyond the initial 64.) If there are two tables, the second table could also have 64 shards, stored on 64 other maxed-out nodes, so the total amount of unique data in the database would be (64 shards/table)×(2 tables)×d. In general, if you have T tables, the maximum amount of unique data that can be stored in the database (i.e. the amount of data before replication) is 64×T×d.

* When you set up storage for your RethinkDB data, you may have to select a filesystem. (Sometimes, the filesystem is already decided by the choice of storage.) We recommend using a filesystem that supports direct I/O (Input/Output). Many compressed or encrypted file systems don't support direct I/O. The ext4 filesystem supports direct I/O (but be careful: if you enable the data=journal mode, then direct I/O support will be disabled; the default is data=ordered). If your chosen filesystem supports direct I/O and you're using Linux, then you don't need to do anything to request or enable direct I/O. RethinkDB does that.

<p style="background-color: lightgrey;">What is direct I/O? It allows RethinkDB to write directly to the storage device (or use its own in-memory caching mechanisms), rather than relying on the operating system's file read and write caching mechanisms. (If you're using Linux, a write-to-file normally writes to the in-memory Page Cache first; only later does that Page Cache get flushed to disk. The Page Cache is also used when reading files.)</p>

* RethinkDB stores its data in a specific directory. You can tell RethinkDB _which_ directory using the RethinkDB config file, as explained below. In this documentation, we assume the directory is `/data`. If you set up a separate device (partition, RAID array, or logical volume) to store the RethinkDB data, then mount that device on `/data`.


## Memory (RAM) Requirements

In their [FAQ](https://rethinkdb.com/faq/), RethinkDB recommends that, "RethinkDB servers have at least 2GB of RAM..." ([source](https://rethinkdb.com/faq/))

In particular: "RethinkDB requires data structures in RAM on each server proportional to the size of the data on that server’s disk, usually around 1% of the size of the total data set." ([source](https://rethinkdb.com/limitations/)) We asked what they meant by "total data set" and [they said](https://github.com/rethinkdb/rethinkdb/issues/5902#issuecomment-230860607) it's "referring to only the data stored on the particular server."

Also, "The storage engine is used in conjunction with a custom, B-Tree-aware caching engine which allows file sizes many orders of magnitude greater than the amount of available memory. RethinkDB can operate on a terabyte of data with about ten gigabytes of free RAM." ([source](https://www.rethinkdb.com/docs/architecture/)) (In this case, it's the _cluster_ which has a total of one terabyte of data, and it's the _cluster_ which has a total of ten gigabytes of RAM. That is, if you add up the RethinkDB RAM on all the servers, it's ten gigabytes.)

In reponse to our questions about RAM requirements, @danielmewes (of RethinkDB) [wrote](https://github.com/rethinkdb/rethinkdb/issues/5902#issuecomment-230860607):

> ... If you replicate the data, the amount of data per server increases accordingly, because multiple copies of the same data will be held by different servers in the cluster.

For example, if you increase the data replication factor from 1 to 2 (i.e. the primary plus one copy), then that will double the RAM needed for metadata. Also from @danielmewes:

> **For reasonable performance, you should probably aim at something closer to 5-10% of the data size.** [Emphasis added] The 1% is the bare minimum and doesn't include any caching. If you want to run near the minimum, you'll also need to manually lower RethinkDB's cache size through the `--cache-size` parameter to free up enough RAM for the metadata overhead...

RethinkDB has [documentation about its memory requirements](https://rethinkdb.com/docs/memory-usage/). You can use that page to get a better estimate of how much memory you'll need. In particular, note that RethinkDB automatically configures the cache size limit to be about half the available memory, but it can be no lower than 100 MB. As @danielmewes noted, you can manually change the cache size limit (e.g. to free up RAM for queries, metadata, or other things).

If a RethinkDB process (on a server) runs out of RAM, the operating system will start swapping RAM out to disk, slowing everything down. According to @danielmewes:

> Going into swap is usually pretty bad for RethinkDB, and RethinkDB servers that have gone into swap often become so slow that other nodes in the cluster consider them unavailable and terminate the connection to them. I recommend adjusting RethinkDB's cache size conservatively to avoid this scenario. RethinkDB will still make use of additional RAM through the operating system's block cache (though less efficiently than when it can keep data in its own cache).


## Filesystem Requirements

RethinkDB "supports most commonly used file systems" ([source](https://www.rethinkdb.com/docs/architecture/)) but it has [issues with BTRFS](https://github.com/rethinkdb/rethinkdb/issues/2781) (B-tree file system).

It's best to use a filesystem that supports direct I/O, because that will improve RethinkDB performance (if you tell RethinkDB to use direct I/O). Many compressed or encrypted filesystems don't support direct I/O.
