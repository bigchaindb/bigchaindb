# Production Node Requirements

Note: This section will be broken apart into several pages, e.g. NTP requirements, RethinkDB requirements, BigchainDB requirements, etc. and those pages will add more details.


## OS Requirements

* RethinkDB Server [will run on any modern OS](https://www.rethinkdb.com/docs/install/). Note that the Fedora package isn't officially supported. Also, official support for Windows is fairly recent ([April 2016](https://rethinkdb.com/blog/2.3-release/)).
* BigchainDB Server requires Python 3.4+ and Python 3.4+ [will run on any modern OS](https://docs.python.org/3.4/using/index.html).
* BigchaindB Server uses the Python `multiprocessing` package and [some functionality in the `multiprocessing` package doesn't work on OS X](https://docs.python.org/3.4/library/multiprocessing.html#multiprocessing.Queue.qsize). You can still use Mac OS X if you use Docker or a virtual machine.

The BigchainDB core dev team uses Ubuntu 14.04, Ubuntu 16.04, Fedora 23, and Fedora 24.

We don't test BigchainDB on Windows or Mac OS X, but you can try.

* If you run into problems on Windows, then you may want to try using Vagrant. One of our community members ([@Mec-Is](https://github.com/Mec-iS)) wrote [a page about how to install BigchainDB on a VM with Vagrant](https://gist.github.com/Mec-iS/b84758397f1b21f21700).
* If you have Mac OS X and want to experiment with BigchainDB, then you could do that [using Docker](../appendices/run-with-docker.html).


## Storage Requirements

When it comes to storage for RethinkDB, there are many things that are nice to have (e.g. SSDs, high-speed input/output [IOPS], replication, reliability, scalability, pay-for-what-you-use), but there are few _requirements_ other than:

1. have enough storage to store all your data (and its replicas), and
2. make sure your storage solution (hardware and interconnects) can handle your expected read & write rates.

For RethinkDB's failover mechanisms to work, [every RethinkDB table must have at least three replicas](https://rethinkdb.com/docs/failover/) (i.e. a primary replica and two others). For example, if you want to store 10 GB of unique data, then you need at least 30 GB of storage. (Indexes and internal metadata are stored in RAM.)

As for the read & write rates, what do you expect those to be for your situation? It's not enough for the storage system alone to handle those rates: the interconnects between the nodes must also be able to handle them.


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
