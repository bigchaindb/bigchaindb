<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Integration testing tools for BigchainDB

## Problem Description
We need a proper way to describe, code, and run integration tests. While we have unit tests to verify the correct behavior of functions and methods, we need a way to easily test a network of BigchainDB nodes.

As an example, we want to make sure that if a valid transaction is pushed to the network, after some time that transaction is stored by more than 2/3 of the nodes; an invalid transaction (malformed, double spent, etc.) pushed to the network must be rejected. This must be true also in different scenarios such as not all nodes are up, or there is latency between the nodes. Note that some of those problems have already been addressed by the Tendermint team.

### Use cases
- Verify we don't break the contract with the user.
- Verify the behavior of the system in case of failure of its services (MongoDB fails, Tendermint fails, BigchainDB fails)
- Verify that some properties of the system are implemented correctly.

## Feature: add a client to manage a BigchainDB network
We define now the characteristics of a new module: the Network Driver, `ND` henceforth. As any other project, it needs a catchy name, but I don't have one in my head now.

The goal of `ND` is to give a simple framework to implement test scenarios that require:
- creating a network
- turn the nodes in the network up or down
- turn the services of a node up or down

There are other useful features we can take into consideration, like:
- creating and pushing transactions to one or more nodes in the network
- check the existence of a transaction in one or more nodes in the network

*Transaction specific* features can be added to `ND` later. We can just use the BigchainDB Python driver for now, or raw `HTTP` requests.

[Bitcoin functional tests](https://github.com/bitcoin/bitcoin/tree/v0.15.0/test/functional) have as similar approach (thanks @codegeschrei for the link).

## Proposed Change
First of all, a new directory will be created, namely `integration-tests`, in the root of the project. This directory will contain the code for `ND`, and will be home for the new integration tests.

Integration tests require not only one node, but a whole network to be up and running. A `docker-compose` configuration file has been created for that purpose, and the `ND` module should leverage it.

The `ND` module implements two main functions:
- network setup, using `docker-compose`
- basic transaction management

In the next sections we will use `ND` to refer to the Python class, and `network` to refer to an instance of it. For now, `network` will most likely be a singleton, since it will control `docker` in the current host. This **will not** be the final name of the module.

### Usage example
The following code is just a suggestion on how the new module shuold be used. It may contain syntax errors or other kind of errors.

```python
def test_valid_transaction_is_available_in_all_nodes(network):
    alice, bob = crypto.generate_key_pair(), crypto.generate_key_pair()
    tx_alice_to_bob = Transaction.create([alice.public_key], [([bob.public_key], 1)])\
                                 .sign([alice.private_key])
    tx = tx.sign([user_priv])
    network.start(4)
    network.node[0].stop()
    requests.post(network.node[1].url + 'transactions', data=json.dumps(tx.to_dict()))
    network.node[0].start()

    time.sleep(1.5)

    for node in network:
        assert requests.get(node.url + 'transactions/' + tx.id) == tx

    network.stop()
```

To facilitate testing and ease the integration with the test framework `pytest`, fixtures will be provided.

### Alternatives
One can argue that the tests should reside in the `tests` directory. This makes sense, but the new test suite has different requirements in terms of fixtures.

[Behavioral Driven Development](https://en.wikipedia.org/wiki/Behavior-driven_development) can be an inspiration for this kind of testing, since it allows to define what is the behavior of the **whole system** given some constraints. Moreover, it's easy to understand since plain English plays a key role. [`pytest-bdd`](https://pypi.python.org/pypi/pytest-bdd) is a plugin for `pytest` that adds fixtures to handle this kind of testing.

### Data model impact
N/A

### API impact
N/A

### Security impact
N/A

### Performance impact
N/A

### End user impact
N/A

### Deployment impact
The new test suite should be deployed in the CI system.

### Documentation impact
The new test suite should be referenced in the documentation.


### Testing impact
N/A


## Implementation

### Assignee(s)
Primary assignee(s): @vrde


### Targeted Release
BigchainDB 2.0


## Dependencies
N/A

## Reference(s)
* [Fixture for acceptance tests](https://github.com/bigchaindb/bigchaindb/pull/1384)
* [Test network Deployment: 4 nodes](https://github.com/bigchaindb/bigchaindb/issues/1922)
