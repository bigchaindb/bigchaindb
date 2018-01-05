# Integration testing simulation

## Problem Description
The integration testing proposal introduced new set of requirements which would require that the infrastructure be controlled at the code level in order to write the tests.


## Proposed Change
The following components shall be required

### Network driver `ND`
The network driver is module which would implement the basic infrastructure management operations which would then be used in test cases to simulate different scenarios.

The `Node` class shall have the following methods:
- `url` : URL to access the BigchainDB node.
- `start()`: Start a node. This api will ensure that all components required for a fully functional node are up and running.
- `stop()`: Stop a given node.
- `reset()`: Reset the state of an existing node i.e. data stored in Tendermint and MongoDB will be purged. **NOTE**: It is only realistic to reset the nodes after all the tests have been executed rather than resetting the network after each test.
- `start_tendermint()`: Run Tendermint process on a given node.
- `stop_tendermint()`: Stop Tendermint process on a given node.
- `configure_tendermint()`: Alter Tendermint configuration on a given node.
- `reset_tendermint()`: Reset Tendermint i.e. `tendermint unsafe_reset_all`.
- `start_db()`: Start MongoDB daemon on a given node.
- `stop_db()`: Stop MongoDB daemon on a given node.
- `reset_db()`: Flush `Bigchain` collection from MongoDB.
- `configure_bigchaindb()`: Update BigchainDB configuration.
- `configure_clock()`: The method should allow to change the clock on a given node. This could facilitate simulation of nodes located in different time zones.
- `configure_QoS()`: Configure different scenarios like network latency, packet loss etc. The underlying implementation could be facilitated via [tc](https://wiki.linuxfoundation.org/networking/netem). 


The network driver implementation could be achieved using the following libraries
- Kubernetes Client: https://github.com/kubernetes-incubator/client-python
- Docker Client: https://github.com/docker/docker-py


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

A detailed list of testing scenarios can be found [here](https://github.com/bigchaindb/bigchaindb/blob/tendermint/proposals/integration-test-cases.md).

### Kubernetes Client resources

- [Create Pod](https://github.com/kubernetes-incubator/client-python/blob/master/kubernetes/docs/CoreV1Api.md#create_namespaced_pod)
- [Delete Pod](https://github.com/kubernetes-incubator/client-python/blob/master/kubernetes/docs/CoreV1Api.md#delete_namespaced_pod)
- [Create Node](https://github.com/kubernetes-incubator/client-python/blob/master/kubernetes/docs/CoreV1Api.md#create_node)
- [Delete Node](https://github.com/kubernetes-incubator/client-python/blob/master/kubernetes/docs/CoreV1Api.md#delete_node)
- [Exec Command post](https://github.com/kubernetes-incubator/client-python/blob/master/kubernetes/docs/CoreV1Api.md#connect_post_namespaced_pod_exec), [Exec Command get](https://github.com/kubernetes-incubator/client-python/blob/master/kubernetes/docs/CoreV1Api.md#connect_get_namespaced_pod_exec)


### Setup integration test environment
Kubernetes can be run locally using `minikube` but the default parameters used when running Kubernetes via `minikube` start a single-node Kubernetes cluster using a virtual machine which results in major resource consumption. This could be avoided by using command line flag, `minikube start --vm-driver=none`. For more details refer [here](https://github.com/kubernetes/minikube#linux-continuous-integration-with-vm-support).


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
The network driver would facilitate the design and implementation of components essential for integration testing. But this introduces Kubernetes as a dependency for tests which should be installed and configured before running tests on Travis CI (refer [here](https://blog.travis-ci.com/2017-10-26-running-kubernetes-on-travis-ci-with-minikube)).



## Implementation

### Assignee(s)
Primary assignee(s): @kansi

### Targeted Release
BigchainDB 2.0


## Dependencies
N/A


## Reference(s)
N/A
