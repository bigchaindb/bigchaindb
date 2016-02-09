# RethinkDB Benchmarks

## Goal

The goal was to test RethinkDB scalability properties, to understand its limits, and to see if we could reach a speed of 1M transactions per second.

## Terminology

### Settings

To test the writing performance of rethinkdb we have a process that inserts a
block in the database in an infinite loop

The block is a valid block with small transactions (transactions without any
payload). The entire block has around 900KB

```python
while True:
    r.table(table).insert(r.json(BLOCK_SERIALIZED), durability='soft').run(conn)
```

In `hard` durability mode, writes are committed to disk before acknowledgments
are sent; in `soft` mode, writes are acknowledged immediately after being stored
in memory.

This means that the insert will block until rethinkdb acknowledges that the data
was cached. In each server we can start multiple process.

### Write units

Lets define `1 write unit` as being 1 process. For example in a 32 node cluster
with each node running 2 processes we would have `64 writes`. This will make it
easier to compare different tests.

### Sharding

Sharding in distributed datastores means partitioning a table so that the data
can be evenly distributed between all nodes in the cluster. In rethinkdb and
most distributed datastores there is a maximum limit of 32 shards per table.

In rethinkdb a `shard` is also called a `primary replica`, since by default the
replication factor is 1. Increasing the replication factor produces `secondary
replicas` that are used for data redundancy (if a node holding a primary replica
goes down another node holding a secondary replica of the same data can step up
and become the primary replica)

For these tests we are using 32 core ec2 instances with SSD storage and 10Gbps
network connections (`c3.8xlarge`). For the tests we used either 32 or 64 node
clusters all running on the same aws region.

These tests show rethinkdb performance and what we can expect from the database.
This does not show the performance of the bigchain

## Tests

### Test 1 

- **number of nodes**: 32
- **number of processes**: 2 processes per node
- **write units**: 32 x 2 = 64 writes
- **output**: stable 1K writes per second

This was the most successful test. We are able to reach a stable output of 1K
blocks per second. The load on the machines is stable and the IO is at an
average of 50-60 %.

Other tests have shown that increasing the number write units per machine can
lead to a stable performance up to 1.5K writes per second but the load on the
nodes would increase until the node would eventually fail. This means that we
are able to handle bursts for a short amount of time (10-20 min).

This test can be used has a baseline for the future in where 64 writes equal 1K
transactions per second. Or that each write unit produces an output of
`1000/64` writes per second, approximately 16 writes per second.


### Test 2

- **number of nodes**: 32
- **number of processes**: 
    - 16 nodes running 2 processes
    - 16 nodes running 3 processes
- **write units**: 16 x 3 + 16 x 2 = 80 writes
- **expected output**: 1250 writes per second
- **output**: stable 1.2K writes per second

Increasing a bit the number of write units shows an increase in output close to
the expected value but in this case the IO around 90 % close to the limit that
the machine can handle.


### Test 3

- **number of nodes**: 32
- **number of processes**: 
    - 16 nodes running 2 processes
    - 16 nodes running 4 processes
- **write units**: 16 x 4 + 16 x 2 = 96 writes
- **expected output**: 1500 writes per second
- **output**: stable 1.4K writes per second

These test produces results similar to previous one. The reason why we don't
reach the expected output may be because rethinkdb needs time to cache results
and at some point increasing the number of write units will not result in an
higher output. Another problem is that as the rethinkdb cache fills (because the
rethinkdb is not able to flush the data to disk fast enough due to IO
limitations) the performance will decrease because the processes will take more
time inserting blocks.


### Test 4

- **number of nodes**: 64
- **number of processes**: 1 process per node
- **write units**: 64 x 1 = 64 writes
- **expected output**: 1000 writes per second
- **output**: stable 1K writes per second

In this case we are increasing the number of nodes in the cluster by 2x. This
won't have an impact in the write performance because the maximum amount of
shards per table in rethinkdb is 32 (rethinkdb will probably increase this limit
in the future). What this provides is more CPU power (and storage for replicas,
more about replication in the next section). We just halved the amount write
units per node maintaining the same output. The IO in the nodes holding the
primary replica is the same has test 1.


### Test 5

- **number of nodes**: 64
- **number of processes**: 2 process per node
- **write units**: 64 x 2 = 128 writes
- **expected output**: 2000 writes per second
- **output**: unstable 2K (peak) writes per second


In this case we are doubling the amount of write units. We are able to reach the
expected output but the output performance is unstable due to the fact that we
reached the IO limit on the machines.


### Test 6


- **number of nodes**: 64
- **number of processes**: 
    - 32 nodes running 1 processes
    - 32 nodes running 2 processes
- **write units**: 32 x 2 + 32 x 1 = 96 writes
- **expected output**: 1500 writes per second
- **output**: stable 1.5K writes per second

This test is similar to Test 3. The only difference is that now the write units
are distributed between 64 nodes meaning that each node is writing to its local
cache and we don't overload the cache of the nodes like we did with Test 3. This
is another advantage of adding more nodes beyond 32.


## Testing replication

Replication is used for data redundancy. In rethinkdb we are able to specify the
number of shards and replicas per table. Data in secondary replicas is no
directly used, its just a mirror of a primary replica and used in case the node
holding the primary replica fails.

Rethinkdb does a good job trying to distribute data evenly between nodes. We ran
some tests to check this.

Note that by increasing the number of replicas we also increase the number of
writes in the cluster. For a replication factor of 2 we double the amount of
writes on the cluster, with a replication factor of 3 we triple the amount of
writes and so on.


With 64 nodes and since we can only have 32 shards we have 32 nodes holding
shards (primary replicas)

With a replication factor of 2 we will have 64 replicas (32 primary replicas and
32 secondary replicas). Since we already have 32 nodes holding the 32
shards/primary replicas rethinkdb uses the other 32 nodes to hold the secondary
replicas. So in a 64 node cluster with 32 shards and a replication factor of 2,
32 nodes will be holding the primary replicas and the other 32 nodes will be holding
the secondary replicas.

With this setup if we run Test 4 now that we have a replication factor of 2 we
will have twice the amount of writes but a nice result is that the IO in the
nodes holding the primary replicas does not increase when compared to Test 4
because all of the excess writing is now being done the 32 nodes holding the
secondary replicas.

Another fact about replication. If I have a 64 node cluster and create a table
with 32 shards, 32 nodes will be holding primary replicas and the other nodes do
not hold any data. If I create another table with 32 shards rethinkdb will
create the shards in the nodes that where not holding any data, evenly
distributing the data.
