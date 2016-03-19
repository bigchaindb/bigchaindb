# BigchainDB Roadmap

See also:

* [Milestones](https://github.com/bigchaindb/bigchaindb/milestones) (i.e. issues to be closed before various releases)
* [Open issues](https://github.com/bigchaindb/bigchaindb/issues) and [open pull requests](https://github.com/bigchaindb/bigchaindb/pulls)

Note: Below, #345 refers to Issue #345 in the BigchainDB repository on GitHub. #N refers to Issue #N.


## Deployment and Federation Configuration/Management
* Define how a federation is managed - [#126](https://github.com/bigchaindb/bigchaindb/issues/126)
* Review current configuration mechanism - [#49](https://github.com/bigchaindb/bigchaindb/issues/49)
* Make the configuration easier for Docker-based setup - [#36](https://github.com/bigchaindb/bigchaindb/issues/36)


## Testing
* (Unit-test writing and unit testing are ongoing.)
* More Integration Testing, Validation Testing, System Testing, Benchmarking
* Define some standard test systems (e.g. local virtual cluster, data center, WAN)
* Develop standardized test descriptions and documentation (test setup, inputs, outputs)
* Build up a suite of tests to test each identified fault
* More tools for cluster benchmarking
* Identify bottlenecks using profiling and monitoring
* Fault-testing framework
* Clean exit for the bigchaindb-benchmark process - [#122](https://github.com/bigchaindb/bigchaindb/issues/122)
* Tool to bulk-upload transactions into biacklog table - [#114](https://github.com/bigchaindb/bigchaindb/issues/114)
* Tool to deploy multiple clients for testing - [#113](https://github.com/bigchaindb/bigchaindb/issues/113)
* Tool to read transactions from files for testing - [#112](https://github.com/bigchaindb/bigchaindb/issues/112)


## Specific Bugs/Faults and Related Tests
* Validation of other nodes
* Changefeed watchdog
* Non-deterministic assignment of tx in S is a DoS vulnerability - [#20](https://github.com/bigchaindb/bigchaindb/issues/20)
* Queues are unbounded - [#124](https://github.com/bigchaindb/bigchaindb/issues/124)
* Better handling of timeouts in block creation - [#123](https://github.com/bigchaindb/bigchaindb/issues/123)
* Secure node-node communication - [#77](https://github.com/bigchaindb/bigchaindb/issues/77)
* Checking if transactions are in a decided_valid block (or otherwise) when necessary - [#134](https://github.com/bigchaindb/bigchaindb/issues/134)
* When validating an incoming transaction, check to ensure it isn't a duplicate - [#131](https://github.com/bigchaindb/bigchaindb/issues/131)
* Consider secondary indexes on some queries - [#105](https://github.com/bigchaindb/bigchaindb/issues/105)


## Transactions / Assets
* Current Top-Level Goal: Define and implement "v2 transactions", that is, support multisig (done) and:
* Support for multiple inputs and outputs - [#128](https://github.com/bigchaindb/bigchaindb/issues/128)
* Crypto-conditions specific to ILP - [#127](https://github.com/bigchaindb/bigchaindb/issues/127)
* Support divisible assets - [#129](https://github.com/bigchaindb/bigchaindb/issues/129)
* Define a JSON template for digital assets - [#125](https://github.com/bigchaindb/bigchaindb/issues/125)
* Revisit timestamps - [#132](https://github.com/bigchaindb/bigchaindb/issues/132)
* Refactor structure of a transaction - [#98](https://github.com/bigchaindb/bigchaindb/issues/98)
* Plugin or hook architecture e.g. for validate_transaction - [#90](https://github.com/bigchaindb/bigchaindb/issues/90)


## Web API (HTTP Client-Server API)
* Current Top-Level Goal: Support v2 transactions (see above)
* Validate the structure of incoming transactions
* Return the correct error code if something goes wrong
* Validate transaction before writing it to the backlog - [#109](https://github.com/bigchaindb/bigchaindb/issues/109)
* Better organization of transaction-related code - [#108](https://github.com/bigchaindb/bigchaindb/issues/108)
* Add an endpoint to query unspents for a given public key
* More endpoints
* See [open issues with the "rest-api" label](https://github.com/bigchaindb/bigchaindb/issues?q=is%3Aissue+is%3Aopen+label%3Arest-api)


## Drivers
* Update the reference driver (Python) to support v2 transactions and web API (see above)
* Drivers/SDKs for more client-side languages (e.g. JavaScript, Ruby, Java)


## Public Sandbox Testnet and Public BigchainDB
* Deploy a 3-node Public Sandbox Testnet in a data center, open to all external users, refreshing daily
* Deploy Public BigchaindB Testnet with more than 3 nodes and with nodes more globally-distributed
* Public BigchainDB governance/voting system
* Transaction (or usage) accounting
* Billing system


## Other
* Get BigchainDB production-ready for submission to AWS Marketplace (as an AMI)


## Future
* Permissions framework
* More Byzantine fault tolerance (BFT)
* Better support for smart contract frameworks
* Algorithm audits
* Protocol audits
* Code (implementation) audits
* Security audits
* IPFS interoperability - [#100](https://github.com/bigchaindb/bigchaindb/issues/100)
* ORM to better-decouple BigchainDB from its data store (will make it easy to try other databases)
* Support more server operating systems
