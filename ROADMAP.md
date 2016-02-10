# BigchainDB Roadmap

## BigchainDB Protocols
* Validation of other nodes
* Byzantine fault tolerance
* Permissions framework
* Benchmarks (e.g. on transactions/second and latency)
* API/Wire protocol exposed by the BigchainDB dameon (HTTP or other). Eventually, the _only_ way for a client to communicate with a BigchainDB database will be via this API.
* Protocol audits including security audits

## Implementation/Code
* Node validation framework (inspect and agree or not with what the other nodes are doing)
* Federation management and monitoring/dashboard
* Packaging, dockerization, AWS image, etc. (i.e. easy deployment options)
* Drivers/SDKs for common client-side languages (e.g. Python, Ruby, JavaScript, Java)
* ORM to better-decouple BigchainDB from its data store (will make it easy to try other databases)
* Code audits including security audits

## Other/Future
* Multisig
* Better support for smart contract frameworks
