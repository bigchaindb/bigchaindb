# BigchainDB - Integration Examples

A scalable blockchain database. [The whitepaper](https://www.bigchaindb.com/whitepaper/) explains what that means.

[![Join the chat at https://gitter.im/bigchaindb/bigchaindb](https://badges.gitter.im/bigchaindb/bigchaindb.svg)](https://gitter.im/bigchaindb/bigchaindb?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Travis branch](https://img.shields.io/travis/diminator/bigchaindb/develop.svg)](https://travis-ci.org/diminator/bigchaindb)
[![Codecov branch](https://img.shields.io/codecov/c/github/diminator/bigchaindb/develop.svg)](https://codecov.io/github/diminator/bigchaindb?branch=develop)

## Interledger

This fork provides basic functionality for supporting the interledger protocol, see http://interledger.org/

The edits are found under interledger/core.py and interledger/tests/test_connector.py
To run the interledger test, [install bigchaindb](#gettingstarted)
```
$0> rethinkdb &

$1> bigchaindb -c examples/interledger/bigchain.json start
$2> bigchaindb -c examples/interledger/megachain.json start

$3> cd examples/interledger
$3> python3 run_cross_ledger_payment_simple.py
```

- [x] multisig
- [x] escrow
- [x] connectors
- [ ] signed receipts
- [ ] receipt propagation and listeners
- [ ] proper asset conversion
- [ ] RESTful API wrapper
- [ ] multi-(big)chain(db) instantiation + network path optimization


## <a name="gettingstarted"></a>Quick Start

### [Install & Run BigchainDB](http://bigchaindb.readthedocs.org/en/develop/installing.html)
### [Run BigchainDB with Docker](http://bigchaindb.readthedocs.org/en/develop/installing.html#run-bigchaindb-with-docker)
### [Getting Started (Tutorial)](http://bigchaindb.readthedocs.org/en/develop/getting-started.html)

## Links for Everyone
* [BigchainDB.com](https://www.bigchaindb.com/) - the main BigchainDB website, including newsletter signup
* [Whitepaper](https://www.bigchaindb.com/whitepaper/) - outlines the motivations, goals and core algorithms of BigchainDB
* [Roadmap](ROADMAP.md)
* [Blog](https://medium.com/the-bigchaindb-blog)
* [Twitter](https://twitter.com/BigchainDB)
* [Google Group](https://groups.google.com/forum/#!forum/bigchaindb)

## Links for Developers
* [Documentation](http://bigchaindb.readthedocs.org/en/develop/#) - for developers
* [CONTRIBUTING.md](CONTRIBUTING.md) - how to contribute
* [Community guidelines](CODE_OF_CONDUCT.md)
* [Open issues](https://github.com/bigchaindb/bigchaindb/issues)
* [Open pull requests](https://github.com/bigchaindb/bigchaindb/pulls)
* [Gitter chatroom](https://gitter.im/bigchaindb/bigchaindb)

## Legal
* [Licenses](LICENSES.md) - open source & open content
* [Imprint](https://www.bigchaindb.com/imprint/)
* [Contact Us](https://www.bigchaindb.com/contact/)
