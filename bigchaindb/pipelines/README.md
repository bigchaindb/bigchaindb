# Overview

Code in this module concerns the long-running processes of BigchainDB.  Some are run as single processes while others may run as many processes in parallel.  When changes are detected in the `backlog`, `block`, or `votes` tables, they are handled here.  Everything is started in [`processes.py`](../processes.py).

All the classes defined in these files depend heavily on the [`multipipes`](https://github.com/bigchaindb/multipipes/) library.  Each contains a static method `create_pipeline` which describes how the `Pipeline` is set up. Consider `votes.py`:

```python
vote_pipeline = Pipeline([
    Node(voter.validate_block),
    Node(voter.ungroup),
    Node(voter.validate_tx, fraction_of_cores=1),
    Node(voter.vote),
    Node(voter.write_vote)
])
```

The process flow is described here: an incoming block is validated, then the transactions are ungrouped, validated individually (using all available cores in parallel), a vote is created, and finally written to the votes table.

## Files

### [`block.py`](./block.py)

Handles inserts and updates to the backlog.  When a node adds a transaction to the backlog, a `BlockPipeline` instance will verify it. If the transaction is valid, it will add it to a new block; otherwise, it's dropped. Finally, after a block accumulates 1000 transactions or a timeout is reached, the process will write the block.

### [`election.py`](./election.py)

Listens for inserts to the vote table. When a new vote comes in, checks if there are enough votes on that block to declare it valid or invalid.  If the block has been elected invalid, the transactions in that block are put back in the backlog.

### [`stale.py`](./stale.py)

Doesn't listen for any changes.  Periodically checks the backlog for transactions that have been there too long and assigns them to a new node if possible.

### [`vote.py`](./vote.py)

Listens for inserts to the bigchain table, then votes the blocks valid or invalid.  When a new block is written, the node running this process checks the validity of the block by checking the validity of each transaction. Then the vote is created based on the block validity, and cast (written) to the votes table.

### [`utils.py`](./utils.py)

Contains the `ChangeFeed` class, an abstraction which combines `multipipes` with the RethinkDB changefeed.
