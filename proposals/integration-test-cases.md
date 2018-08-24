<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Integration test case suggestions
This document gives an overview of possible integration test cases, provides some useful links and a specification how to write the Python `docstring` for a test case.


## Useful links
- testing advice by [bitcoin](https://github.com/bitcoin/bitcoin/tree/master/test/functional#general-test-writing-advice)

- [tendermint](https://github.com/tendermint/tendermint/tree/master/test) integration tests


## How to structure a test scenario
The following serves as a structure to describe the tests. Each integration test should contain this description in the docstring.

| Keyword               | Description               |
|-----------------------|---------------------------|
| Name                  | Name of the test          |
| Startup State         | Required base settings    |
| Test Description      | Steps to be executed      |
| Output Specification  | Expected output           |

### Startup State
The startup state specifies the system at the beginning of a test. Some questions that need to be answered:
- How many nodes will be running?
- What is the state of each node?
- Are there any faulty nodes?
- Is there any initial data setup?
  - e.g. are there existing transactions?

### Test description
Write down the steps that are executed during the tests.

### Output Specification
This specification describes the state of the system at the end of the test. The questions in the startup state can be used.

### Example Docstring
```
def test_node_count(some_args):
    """
    Name: Test Node Count
    Startup State: None
    Test Description: Start the system with 4 Nodes
    Output Specification: Every node has N-1 other peers
    """
 ```

## Scenario groups and test case suggestions
### Starting
- start n nodes, all are visible -> assert everyone has N-1 other peers
- start n nodes, one crashes, node count changes
- start nodes with different versions of bdb
### Syncing
- start n nodes, get sync, all have the same
- start n nodes, different sync, bft ok
- start n nodes, different sync, bft fails
- start n nodes, give initial blockchain and check if everyone has the correct status
- start n nodes, give initial blockchain, some faulty nodes, check status
- start n nodes, how long should sync take (timeout?)
### Crash nodes
- start n nodes, ones freezes, what is supposed to happen?
- start n nodes, one crashes, comes up, correct sync
- start n nodes, crash all, come up, correct status
### Crash components
- start n nodes, mongodb crashes
- start n nodes, tendermint crashes
- start n nodes, bigchain crashes
- start n nodes, connection crashes
- what else can crash?
- possible crash times
  - on startup
  - when running and nodes are synced
  - on sync
  - on send tx
  - on new block
  - on vote
### System settings
- start n nodes, have different times in nodes (timestamps)
- clock drifting (timejacking)
- start n nodes, have one key not in the keyring
### Transactions
- start n nodes, one sends tx, sync
- start n nodes, n nodes send a tx, sync
- start n nodes, one tries to double spend
- start n nodes, one sends tx, new node up, sees tx
- start n nodes, one sends divisible tx for two other nodes
### Validation
- start n nodes, check app hash
- start n nodes, check app hash, one crashes, gets up, check hash
- nodes validate tx
### Voting
- n nodes vote, bft scenarios
### Blocks
- start n nodes, one creates a block
- start n nodes, check block height, new block, check block height
- have an invalid block (new block, wrong hash?)
- have block bigger than max size
### Query
- start n nodes, let all query for the same block
- query tx
### Malicious nodes
- start n nodes, one manipulates the blockchain
### Events
- start n nodes, let one check for event stream of another
