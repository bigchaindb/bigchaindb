# BigchainDB Roadmap

## BigchainDB Protocols
* Validation of other nodes
* Fault tolerance
* Permissions framework
* Protocol audits including security audits

## HTTP Client-Server API
* Validate the structure of the transaction
* Return the correct error code if something goes wrong
* Add an endpoint to query unspents for a given public key
* More endpoints
* See [the relevant open issues](https://github.com/bigchaindb/bigchaindb/issues?q=is%3Aissue+is%3Aopen+label%3Arest-api)

## Implementation/Code
* Node validation framework (inspect and agree or not with what the other nodes are doing)
* Open public testing cluster (for people to try out a BigchainDB cluster and to test client software)
* Federation management tools
* More tools for benchmarking a cluster
* Descriptions and results of more benchmarking tests
* AWS image and other easy deployment options
* Drivers/SDKs for more client-side languages (e.g. JavaScript, Ruby, Java)
* ORM to better-decouple BigchainDB from its data store (will make it easy to try other databases)
* Code audits including security audits

## Other/Future
* Byzantine fault tolerance
* Better support for smart contract frameworks

## Done/Past (i.e. was in the Roadmap)
* Packaging for PyPI (setup.py etc.) - [the latest version release can be found on PyPI](https://pypi.python.org/pypi/BigchainDB)
* Dockerization
* Monitoring/dashboard - initial vesion added in [Pull Request #72](https://github.com/bigchaindb/bigchaindb/pull/72)
* API/Wire protocol (RESTful HTTP API) - initial version added in [Pull Request #102](https://github.com/bigchaindb/bigchaindb/pull/102)
* Python driver/SDK - initial version added in [Pull Request #102](https://github.com/bigchaindb/bigchaindb/pull/102)
* Multisig support - initial version added in [Pull Request #107](https://github.com/bigchaindb/bigchaindb/pull/107)
