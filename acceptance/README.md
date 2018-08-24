<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Acceptance test suite
This directory contains the acceptance test suite for BigchainDB.

The suite uses Docker Compose to set up a single BigchainDB node, run all tests, and finally stop the node. In the future we will add support for a four node network setup.

## Running the tests
It should be as easy as `make test-acceptance`.

Note that `make test-acceptance` will take some time to start the node and shutting it down. If you are developing a test, or you wish to run a specific test in the acceptance test suite, first start the node with `make start`. After the node is running, you can run `pytest` inside the `python-acceptance` container with:

```bash
docker-compose run --rm python-acceptance pytest <use whatever option you need>
```

## Writing and documenting the tests
Tests are sometimes difficult to read. For acceptance tests, we try to be really explicit on what the test is doing, so please write code that is *simple* and easy to understand. We decided to use literate-programming documentation. To generate the documentation run:

```bash
make doc-acceptance
```
