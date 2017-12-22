# Integration testing simulation

## Problem Description
The integration testing proposal introduced new set of requirements which would require that the infrastructure be controlled at the code level in order to write the tests.


## Proposed Change
The following components shall be required

### Network driver `ND`
The network driver is module which would implement the basic infrastructure management operations which would then be used in test cases to simulate different scenarios.

The `Node` class shall have the following methods:
- `url`
- `start()`
- `stop()`
- `start_tendermint()`
- `stop_tendermint()`
- `configure_tendermint()`
- `reset_tendermint()`
- `start_db()`
- `stop_db()`
- `reset_db()`
- `configure_bigchaindb()`
- `configure_clock()`
- `configure_QoS()` (discussed later)


`configure_clock()`: This method should allow to change the clock on a given node. This could facilitate simulation of nodes located in different time zones.

`configure_QoS()`: This methods allows configuring different scenarios like network latency, packet loss etc. The underlying implementation could be facilitated via [tc](https://wiki.linuxfoundation.org/networking/netem). 


The network driver implementation could be achieved using the following libraries
- https://github.com/kubernetes-incubator/client-python
- https://github.com/docker/docker-py


### Usage example

```python
def test_valid_transaction_is_synced_nodes(network):
    alice, bob = crypto.generate_key_pair(), crypto.generate_key_pair()
    tx_alice_to_bob = Transaction.create([alice.public_key], [([bob.public_key], 1)])\
                                 .sign([alice.private_key])
    tx = tx.sign([user_priv])
    network.start(4)
    network.nodes[0].stop()
    requests.post(network.node[1].url + 'transactions', data=json.dumps(tx.to_dict()))
    network.node[0].start()

    time.sleep(1.5)

    for node in network.nodes:
        assert requests.get(node.url + 'transactions/' + tx.id) == tx

    network.stop()
```


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
N/A

### Documentation impact
N/A

### Testing impact
The network driver would facilitate the design and implementation of components essential for integration testing.


## Implementation

### Assignee(s)
Primary assignee(s): @kansi

### Targeted Release
BigchainDB 2.0


## Dependencies
N/A


## Reference(s)
N/A
