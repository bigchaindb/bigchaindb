# Node Requirements (OS, Memory, Storage, etc.)

For now, we will assume that a BigchainDB node is just one server. In the future, a node may consist of several closely-coupled servers run by one node operator (federation member).


## OS Requirements

* RethinkDB Server [will run on any modern OS](https://www.rethinkdb.com/docs/install/). Note that the Fedora package isn't officially supported. Also, official support for Windows is fairly recent ([April 2016](https://rethinkdb.com/blog/2.3-release/)).
* Python 3.4+ [will run on any modern OS](https://docs.python.org/3.4/using/index.html).
* [Some functionality in the `multiprocessing` package doesn't work on OS X](https://docs.python.org/3.4/library/multiprocessing.html#multiprocessing.Queue.qsize). You can still use Mac OS X if you use Docker or a virtual machine.
* ZeroMQ [will run on any modern OS](http://zeromq.org/area:download).

The BigchainDB core dev team uses Ubuntu 14.04 or Fedora 23.

We don't test BigchainDB on Windows or Mac OS X, but you can try.

* If you run into problems on Windows, then you may want to try using Vagrant. One of our community members ([@Mec-Is](https://github.com/Mec-iS)) wrote [a page about how to install BigchainDB on a VM with Vagrant](https://gist.github.com/Mec-iS/b84758397f1b21f21700).
* If you have Mac OS X and want to experiment with BigchainDB, then you could do that [using Docker](run-with-docker.html).


## Storage Requirements

When it comes to storage for RethinkDB, there are many things that are nice to have (e.g. SSDs, high-speed input/output [IOPS], replication, reliability, scalability, pay-for-what-you-use), but there are few _requirements_ other than:

1. have enough storage to store all your data (and its replicas), and
2. make sure your storage solution (hardware and interconnects) can handle your expected read & write rates.

For RethinkDB's failover mechanisms to work, [every RethinkDB table must have at least three replicas](https://rethinkdb.com/docs/failover/) (i.e. a primary replica and two others). For example, if you want to store 10 GB of unique data, then you need at least 30 GB of storage. (Indexes and internal metadata are stored in RAM.)

As for the read & write rates, what do you expect those to be for your situation? It's not enough for the storage system alone to handle those rates: the interconnects between the nodes must also be able to handle them.


## Memory (RAM) Requirements

In their [FAQ](https://rethinkdb.com/faq/), RethinkDB recommends that, "RethinkDB servers have at least 2GB of RAM... RethinkDB has a custom caching engine and can run on low-memory nodes with large amounts of on-disk data..." ([source](https://rethinkdb.com/faq/))

In particular: "RethinkDB requires data structures in RAM on each server proportional to the size of the data on that server’s disk, usually around 1% of the size of the total data set." ([source](https://rethinkdb.com/limitations/))

Also, "The storage engine is used in conjunction with a custom, B-Tree-aware caching engine which allows file sizes many orders of magnitude greater than the amount of available memory. RethinkDB can operate on a terabyte of data with about ten gigabytes of free RAM." ([source](https://www.rethinkdb.com/docs/architecture/))

RethinkDB has [documentation about its memory requirements](https://rethinkdb.com/docs/memory-usage/). You can use that page to get a better estimate of how much memory you'll need.


## Filesystem Requirements

RethinkDB "supports most commonly used file systems" ([source](https://www.rethinkdb.com/docs/architecture/)) but it has [issues with BTRFS](https://github.com/rethinkdb/rethinkdb/issues/2781) (B-tree file system).

It's best to use a filesystem that supports direct I/O, because that will improve RethinkDB performance (if you tell RethinkDB to use direct I/O). Many compressed or encrypted filesystems don't support direct I/O.
