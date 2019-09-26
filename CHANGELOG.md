<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Change Log (Release Notes)

All _notable_ changes to this project will be documented in this file (`CHANGELOG.md`).

This project adheres to [the Python form of Semantic Versioning](https://packaging.python.org/tutorials/distributing-packages/#choosing-a-versioning-scheme) (or at least we try). The BigchainDB public API _was_ defined in this file but that definition was moved and can now be found in [BEP-7](https://github.com/bigchaindb/BEPs/tree/master/7).

Contributors to this file, please follow the guidelines on [keepachangelog.com](http://keepachangelog.com/). Note that each version (or "release") is the name of a [Git _tag_](https://git-scm.com/book/en/v2/Git-Basics-Tagging) of a particular commit, so the associated date and time are the date and time of that commit (as reported by GitHub), _not_ the "Uploaded on" date listed on PyPI (which may differ).

For reference, the possible headings are:

* **Added** for new features.
* **Changed** for changes in existing functionality.
* **Deprecated** for once-stable features removed in upcoming releases.
* **Removed** for deprecated features removed in this release.
* **Fixed** for any bug fixes.
* **Security** to invite users to upgrade in case of vulnerabilities.
* **External Contributors** to list contributors outside of BigchainDB GmbH.
* **Known Issues**
* **Notes**

## [2.0] - 2019-09-26

### Changed

Migrated from Tendermint 0.22.8 to 0.31.5.

## [2.0 Beta 9] - 2018-11-27

### Changed

Removed support for TLSv1 and TLSv1.1 in all NGINX config files. Kept support for TLSv1.2 and added support for TLSv1.3. [Pull Request #2601](https://github.com/bigchaindb/bigchaindb/pull/2601)

### Fixed

Fixed two issues with schema validation. Pull requests [#2606](https://github.com/bigchaindb/bigchaindb/pull/2606) & [#2607](https://github.com/bigchaindb/bigchaindb/pull/2607)

### External Contributors

[@gamjapark](https://github.com/gamjapark) and team translated all the [BigchainDB root docs](https://docs.bigchaindb.com/en/latest/korean/index.html) into Korean. [Pull Request #2603](https://github.com/bigchaindb/bigchaindb/pull/2603)

## [2.0 Beta 8] - 2018-11-03

### Changed

* Revised the [Simple Deployment Template](http://docs.bigchaindb.com/projects/server/en/latest/simple-deployment-template/index.html) in the docs. Added NGINX to the mix. Pull Requests [#2578](https://github.com/bigchaindb/bigchaindb/pull/2578) and [#2579](https://github.com/bigchaindb/bigchaindb/pull/2579)
* Revised `nginx/nginx.conf` to enable CORS. [Pull Request #2580](https://github.com/bigchaindb/bigchaindb/pull/2580)

### Fixed

* Fixed a typo in the Kubernetes ConfigMap template. [Pull Request #2583](https://github.com/bigchaindb/bigchaindb/pull/2583)

### External Contributors

[@gamjapark](https://github.com/gamjapark) translated the main `README.md` file into Korean. [Pull Request #2592](https://github.com/bigchaindb/bigchaindb/pull/2592)

## [2.0 Beta 7] - 2018-09-28

Tag name: v2.0.0b7

### Added

Completed the implementation of chain-migration elections (BEP-42). Pull requests [#2553](https://github.com/bigchaindb/bigchaindb/pull/2553), [#2556](https://github.com/bigchaindb/bigchaindb/pull/2556), [#2558](https://github.com/bigchaindb/bigchaindb/pull/2558), [#2563](https://github.com/bigchaindb/bigchaindb/pull/2563) and [#2566](https://github.com/bigchaindb/bigchaindb/pull/2566)

### Changed

* Code that used the Python driver's (deprecated) transactions.send() method now uses its transactions.send_commit() method instead. [Pull request #2547](https://github.com/bigchaindb/bigchaindb/pull/2547)
* Code that implied pluggable "consensus" now implies pluggable transaction "validation" (a more accurate word). [Pull request #2561](https://github.com/bigchaindb/bigchaindb/pull/2561)

### Removed

Benchmark logs. [Pull request #2565](https://github.com/bigchaindb/bigchaindb/pull/2565)

### Fixed

A bug caused by an incorrect MongoDB query. [Pull request #2567](https://github.com/bigchaindb/bigchaindb/pull/2567)

### Notes

There's now better documentation about logs, log rotation, and the `server.bind` config setting. Pull requests [#2546](https://github.com/bigchaindb/bigchaindb/pull/2546) and [#2575](https://github.com/bigchaindb/bigchaindb/pull/2575)

## [2.0 Beta 6] - 2018-09-17

Tag name: v2.0.0b6

### Added

* [New documentation about privacy and handling private data](https://docs.bigchaindb.com/en/latest/private-data.html). [Pull request #2437](https://github.com/bigchaindb/bigchaindb/pull/2437)
* New documentation about log rotation. Also rotate Tendermint logs if started using Monit. [Pull request #2528](https://github.com/bigchaindb/bigchaindb/pull/2528)
* Began implementing one of the migration strategies outlined in [BEP-42](https://github.com/bigchaindb/BEPs/tree/master/42). That involved creating a more general-purpose election process and commands. Pull requests [#2488](https://github.com/bigchaindb/bigchaindb/pull/2488), [#2495](https://github.com/bigchaindb/bigchaindb/pull/2495), [#2498](https://github.com/bigchaindb/bigchaindb/pull/2498), [#2515](https://github.com/bigchaindb/bigchaindb/pull/2515), [#2535](https://github.com/bigchaindb/bigchaindb/pull/2535)
* Used memoization to avoid doing some validation checks multiple times. [Pull request #2490](https://github.com/bigchaindb/bigchaindb/pull/2490)
* Created an all-in-one Docker image containing BigchainDB Server, Tendermint and MongoDB. It was created for a particular user and is not recommended for production use unless you really know what you're doing. [Pull request #2424](https://github.com/bigchaindb/bigchaindb/pull/2424)

### Changed

* The supported versions of Tendermint are now hard-wired into BigchainDB Server: it checks to see what version the connected Tendermint has, and if it's not compatible, BigchainDB Server exits with an error message. [Pull request #2541](https://github.com/bigchaindb/bigchaindb/pull/2541)
* The docs no longer say to install the highest version of Tendermint: they say to install a specific version. [Pull request #2524](https://github.com/bigchaindb/bigchaindb/pull/2524)
* The setup docs include more recommended settings for `config.toml`. [Pull request #2516](https://github.com/bigchaindb/bigchaindb/pull/2516)
* The process to add, remove or update the voting power of a validator at run time (using the `bigchaindb upsert-validator` subcommands) was completely changed and is now fully working. See [issue #2372](https://github.com/bigchaindb/bigchaindb/issues/2372) and all the pull requests it references. Pull requests [#2439](https://github.com/bigchaindb/bigchaindb/pull/2439) and [#2440](https://github.com/bigchaindb/bigchaindb/pull/2440)
* The license on the documentation was changed from CC-BY-SA-4 to CC-BY-4. [Pull request #2427](https://github.com/bigchaindb/bigchaindb/pull/2427)
* Re-activated and/or updated some unit tests that had been deacivated during the migration to Tendermint. Pull requests [#2390](https://github.com/bigchaindb/bigchaindb/pull/2390), [#2415](https://github.com/bigchaindb/bigchaindb/pull/2415), [#2452](https://github.com/bigchaindb/bigchaindb/pull/24), [#2456](https://github.com/bigchaindb/bigchaindb/pull/2456)
* Updated RapidJSON to a newer, faster version. [Pull request #2470](https://github.com/bigchaindb/bigchaindb/pull/2470)
* The Java driver is now officially supported. [Pull request #2478](https://github.com/bigchaindb/bigchaindb/pull/2478)
* The MongoDB indexes on transaction id and block height were changed to be [unique indexes](https://docs.mongodb.com/manual/core/index-unique/). [Pull request #2492](https://github.com/bigchaindb/bigchaindb/pull/2492)
* Updated the required `cryptoconditions` package to a newer one. [Pull request #2494](https://github.com/bigchaindb/bigchaindb/pull/2494)

### Removed

* Removed some old code and tests. Pull requests
  [#2374](https://github.com/bigchaindb/bigchaindb/pull/2374),
  [#2452](https://github.com/bigchaindb/bigchaindb/pull/2452),
  [#2474](https://github.com/bigchaindb/bigchaindb/pull/2474),
  [#2476](https://github.com/bigchaindb/bigchaindb/pull/2476),
  [#2491](https://github.com/bigchaindb/bigchaindb/pull/2491)

### Fixed

* Fixed the Events API so that it only sends valid transactions to subscribers. Also changed how it works internally, so now it is more reliable. [Pull request #2529](https://github.com/bigchaindb/bigchaindb/pull/2529)
* Fixed a bug where MongoDB database initialization would abort if a collection already existed. [Pull request #2520](https://github.com/bigchaindb/bigchaindb/pull/2520)
* Fixed a unit test that was failing randomly. [Pull request #2423](https://github.com/bigchaindb/bigchaindb/pull/2423)
* Fixed the validator curl port. [Pull request #2447](https://github.com/bigchaindb/bigchaindb/pull/2447)
* Fixed an error in the docs about the HTTP POST /transactions endpoint. [Pull request #2481](https://github.com/bigchaindb/bigchaindb/pull/2481)
* Fixed a unit test that could loop forever. [Pull requqest #2486](https://github.com/bigchaindb/bigchaindb/pull/2486)
* Fixed a bug when validating a CREATE + TRANSFER. [Pull request #2487](https://github.com/bigchaindb/bigchaindb/pull/2487)
* Fixed the HTTP response when posting a transaction in commit mode. [Pull request #2510](https://github.com/bigchaindb/bigchaindb/pull/2510)
* Fixed a crash that happened when attempting to restart BigchainDB at Tendermint block height 1. [Pull request#2519](https://github.com/bigchaindb/bigchaindb/pull/2519)

### External Contributors

@danacr - [Pull request #2447](https://github.com/bigchaindb/bigchaindb/pull/2447)

### Notes

The docs section titled "Production Deployment Template" was renamed to "Kubernetes Deployment Template" and we no longer consider it the go-to deployment template. The "Simple Deployment Template" is simpler, easier to understand, and less expensive (unless you are with an organization that already has a big Kubernetes cluster).

## [2.0 Beta 5] - 2018-08-01

Tag name: v2.0.0b5

### Changed

* Supported version of Tendermint `0.22.3` -> `0.22.8`. [Pull request #2429](https://github.com/bigchaindb/bigchaindb/pull/2429).

### Fixed

* Stateful validation raises a DoubleSpend exception if there is any other transaction that spends the same output(s) even if it has the same transaction ID. [Pull request #2422](https://github.com/bigchaindb/bigchaindb/pull/2422).

## [2.0 Beta 4] - 2018-07-30

Tag name: v2.0.0b4

### Added

- Added scripts for creating a configuration to manage processes with Monit. [Pull request #2410](https://github.com/bigchaindb/bigchaindb/pull/2410).

### Fixed

- Redundant asset and metadata queries were removed. [Pull request #2409](https://github.com/bigchaindb/bigchaindb/pull/2409).
- Signal handling was fixed for BigchainDB processes. [Pull request #2395](https://github.com/bigchaindb/bigchaindb/pull/2395).
- Some of the abruptly closed sockets that used to stay in memory are being cleaned up now. [Pull request 2408](https://github.com/bigchaindb/bigchaindb/pull/2408).
- Fixed the bug when WebSockets powering Events API became unresponsive. [Pull request #2413](https://github.com/bigchaindb/bigchaindb/pull/2413).

### Notes:

* The instructions on how to write a BEP were simplified. [Pull request #2347](https://github.com/bigchaindb/bigchaindb/pull/2347).
* A section about troubleshooting was added to the network setup guide. [Pull request #2398](https://github.com/bigchaindb/bigchaindb/pull/2398).
* Some of the core code was given a better package structure. [Pull request #2401](https://github.com/bigchaindb/bigchaindb/pull/2401).
* Some of the previously disabled unit tests were re-enabled and updated. Pull requests [#2404](https://github.com/bigchaindb/bigchaindb/pull/2404) and [#2402](https://github.com/bigchaindb/bigchaindb/pull/2402).
* Some building blocks for dynamically adding new validators were introduced. [Pull request #2392](https://github.com/bigchaindb/bigchaindb/pull/2392).

## [2.0 Beta 3] - 2018-07-18

Tag name: v2.0.0b3

### Fixed

Fixed a bug in transaction validation. For some more-complex situations, it would say that a valid transaction was invalid. This bug was actually fixed before; it was [issue #1271](https://github.com/bigchaindb/bigchaindb/issues/1271). The unit test for it was turned off while we integrated Tendermint. Then the query implementation code got changed, reintroducing the bug, but the unit test was off so the bug wasn't caught. When we turned the test back on, shortly after releasing Beta 2, it failed, unveiling the bug. [Pull request #2389](https://github.com/bigchaindb/bigchaindb/pull/2389)

## [2.0 Beta 2] - 2018-07-16

Tag name: v2.0.0b2

### Added

* Added new configuration settings `tendermint.host` and `tendermint.port`. [Pull request #2342](https://github.com/bigchaindb/bigchaindb/pull/2342)
* Added tests to ensure that BigchainDB gracefully handles "nasty" strings in keys and values. [Pull request #2334](https://github.com/bigchaindb/bigchaindb/pull/2334)
* Added a new logging handler to capture benchmark stats to a separate file. [Pull request #2349](https://github.com/bigchaindb/bigchaindb/pull/2349)

### Changed

* Changed the names of BigchainDB processes (Python processes) to include 'bigchaindb', so they are easier to spot and find. [Pull request #2354](https://github.com/bigchaindb/bigchaindb/pull/2354)
* Updated all code to support the latest version of Tendermint. Note that the BigchainDB ABCI server now listens to port 26657 instead of 46657. Pull requests [#2375](https://github.com/bigchaindb/bigchaindb/pull/2375) and [#2380](https://github.com/bigchaindb/bigchaindb/pull/2380)

### Removed

Removed all support and code for the old backlog_reassign_delay setting. [Pull request #2332](https://github.com/bigchaindb/bigchaindb/pull/2332)

### Fixed

* Fixed a bug that sometimes arose when using Docker Compose. (Tendermint would freeze.) [Pull request #2341](https://github.com/bigchaindb/bigchaindb/pull/2341)
* Fixed a bug in the code that creates a MongoDB index for the "id" in the transactions collection. It works now, and performance is improved. [Pull request #2378](https://github.com/bigchaindb/bigchaindb/pull/2378)
* The logging server would keep runnning in some tear-down scenarios. It doesn't do that any more. [Pull request #2304](https://github.com/bigchaindb/bigchaindb/pull/2304)

### External Contributors

@hrntknr - [Pull request #2331](https://github.com/bigchaindb/bigchaindb/pull/2331)

### Known Issues

The `bigchaindb upsert-validator` subcommand is not working yet, but a solution ([BEP-21](https://github.com/bigchaindb/BEPs/tree/master/21)) has been finalized and will be implemented before we release the final BigchainDB 2.0.

### Notes

* A lot of old/dead code was deleted. Pull requests
[#2319](https://github.com/bigchaindb/bigchaindb/pull/2319),
[#2338](https://github.com/bigchaindb/bigchaindb/pull/2338),
[#2357](https://github.com/bigchaindb/bigchaindb/pull/2357),
[#2365](https://github.com/bigchaindb/bigchaindb/pull/2365),
[#2366](https://github.com/bigchaindb/bigchaindb/pull/2366),
[#2368](https://github.com/bigchaindb/bigchaindb/pull/2368) and
[#2374](https://github.com/bigchaindb/bigchaindb/pull/2374)
* Improved the documentation page "How to setup a BigchainDB Network". [Pull Request #2312](https://github.com/bigchaindb/bigchaindb/pull/2312)

## [2.0 Beta 1] - 2018-06-01

Tag name: v2.0.0b1

### Fixed

* Fixed a bug that arose with some code that treated transactions-waiting-for-block-inclusion as if they were already stored in MongoDB (i.e. already in a block). [Pull request #2318](https://github.com/bigchaindb/bigchaindb/pull/2318)
* If a user asked for a block and it happened to be an empty block, BigchainDB returned 404 Not Found, as if the block did not exist. Now it returns a 200 OK with a block containing no transactions, i.e. an empty block. [Pull request #2321](https://github.com/bigchaindb/bigchaindb/pull/2321)

### Known Issues

* An issue was found with the `bigchaindb upsert-validator` command. A solution was proposed in [BEP-19](https://github.com/bigchaindb/BEPs/pull/45) and is being implemented in [pull request #2314](https://github.com/bigchaindb/bigchaindb/pull/2314)
* If you run BigchainDB locally using `make start` (i.e. using Docker Compose) and then you put the node under heavy write load, Tendermint can become unresponsive and running `make stop` can hang.
* There seems to be one or more issues with Tendermint when it is put under heavy load (i.e. even when BigchainDB isn't involved). See Tendermint issues [#1394](https://github.com/tendermint/tendermint/issues/1394), [#1642](https://github.com/tendermint/tendermint/issues/1642) and [#1661](https://github.com/tendermint/tendermint/issues/1661)

### Notes

* There's a [new docs page](https://docs.bigchaindb.com/projects/server/en/v2.0.0b1/simple-network-setup.html) about how to set up a network where each node uses a single virtual machine.
* We checked, and BigchainDB 2.0 Beta 1 works with MongoDB 3.6 (and 3.4).
* Support for RethinkDB is completely gone.

## [2.0 Alpha 6] - 2018-05-17

Tag name: v2.0.0a6

### Changed

Upgraded PyMongo to version 3.6 (which is compatible with MongoDB 3.6, 3.4 [and more](https://docs.mongodb.com/ecosystem/drivers/driver-compatibility-reference/#python-driver-compatibility)). [Pull request #2298](https://github.com/bigchaindb/bigchaindb/pull/2298)

### Fixed

When deploying a node using our Docker Compose file, it didn't expose port 46656, which is used by Tendermint for inter-node communications, so the node couldn't communicate with other nodes. We fixed that in [pull request #2299](https://github.com/bigchaindb/bigchaindb/pull/2299)

### Notes

We ran all our tests using MongoDB 3.6 and they all passed, so it seems safe to use BigchainDB with MongoDB 3.6 from now on.

## [2.0 Alpha 5] - 2018-05-11

Tag name: v2.0.0a5

### Changed

To resolve [issue #2279](https://github.com/bigchaindb/bigchaindb/issues/2279), we made some changes to the `bigchaindb-abci` package (which is our fork of `py-abci`) and told BigchainDB to use the new version (`bigchaindb-abci==0.4.5`). [Pull request #2281](https://github.com/bigchaindb/bigchaindb/pull/2281).

## [2.0 Alpha 4] - 2018-05-09

Tag name: v2.0.0a4

### Changed

The Kubernetes liveness probe for the BigchainDB StatefulSet was improved to check the Tendermint /status endpoint in addition to the Tendermint /abci_info endpoint. [Pull request #2275](https://github.com/bigchaindb/bigchaindb/pull/2275)

### Fixed

[Pull request #2270](https://github.com/bigchaindb/bigchaindb/pull/2270) resolved [issue #2269](https://github.com/bigchaindb/bigchaindb/issues/2269).

### Notes

There's a new [page in the docs about storing files in BigchainDB](https://docs.bigchaindb.com/en/latest/store-files.html). [Pull request #2259](https://github.com/bigchaindb/bigchaindb/pull/2259)

## [2.0 Alpha 3] - 2018-05-03

Tag name: v2.0.0a3

### Changed

* Upgraded BigchainDB Server code to use the latest version of Tendermint: version 0.19.2. Pull requests [#2249](https://github.com/bigchaindb/bigchaindb/pull/2249), [#2252](https://github.com/bigchaindb/bigchaindb/pull/2252) and [#2253](https://github.com/bigchaindb/bigchaindb/pull/2253)
* Made some fixes to `py-abci` (an external Python package) and used our fixed version with BigchainDB. Those fixes resolved several known issues, including [issue #2182](https://github.com/bigchaindb/bigchaindb/issues/2182) and issues with large transactions in general. Note: At the time of writing, our fixes to `py-abci` hadn't been merged into the main `py-abci` repository or its latest release on PyPI; we were using our own special `bigchaindb-abci` package (which included our fixes). Pull requests [#2250](https://github.com/bigchaindb/bigchaindb/pull/2250) and [#2261](https://github.com/bigchaindb/bigchaindb/pull/2261)
* If BigchainDB Server crashes and then comes back, Tendermint Core doesn't try to reconnect to it. That's just how Tendermint Core works. We revised our Kubernetes-based production deployment template to resolve that issue: BigchainDB Server and Tendermint Core are now in the same Kubernetes StatefulSet; if the connection between them ever goes down, then Kubernetes restarts the whole StatefulSet. [Pull request #2242](https://github.com/bigchaindb/bigchaindb/pull/2242)

### Fixed

Re-enabled multi-threading. [Pull request #2258](https://github.com/bigchaindb/bigchaindb/pull/2258)

### Known Issues

Tendermint changed how it responds to a request to store data (via the [Tendermint Broadcast API](https://tendermint.com/docs/tendermint-core/using-tendermint.html#broadcast-api)) between version 0.12 and 0.19.2. We started modifying the code of BigchainDB Server to account for those changes in responses (in [pull request #2239](https://github.com/bigchaindb/bigchaindb/pull/2239)), but we found that there's a difference between what the Tendermint documentation _says_ about those responses and how Tendermint actually responds. We need to determine Tendermint's intent before we can finalize that pull request.

### Notes

We were focused on getting the public BigchainDB Testnet stable during the development of BigchainDB 2.0 Alpha 3, and we think we largely succeeded. Because of that focus, we delayed the deployment of an internal test network until later. It would have had the same instabilities as the public BigchainDB Testnet anyway. In the future, we'll always test a new version of BigchainDB on our internal test network before deploying it on the public BigchainDB Testnet. (That wasn't possible this time around, because there was no old/stable version of BigchainDB 2.n to run on the public BigchainDB Testnet while we tested BigchainDB 2.[n+1] internally.)

## [2.0 Alpha 2] - 2018-04-18

Tag name: v2.0.0a2

### Added

An implementation of [BEP-8 (BigchainDB Enhancement Proposal #8)](https://github.com/bigchaindb/BEPs/tree/master/8), which makes sure a node can recover from a system fault (e.g. a crash) into a consistent state, i.e. a state where the data in the node's local MongoDB database is consistent with the data stored in the blockchain. Pull requests [#2135](https://github.com/bigchaindb/bigchaindb/pull/2135) and [#2207](https://github.com/bigchaindb/bigchaindb/pull/2207)

### Changed

When someone uses the HTTP API to send a new transaction to a BigchainDB network using the [POST /api/v1/transactions?mode={mode}](https://docs.bigchaindb.com/projects/server/en/master/http-client-server-api.html#post--api-v1-transactions?mode=mode) endpoint, they now get back a more informative HTTP response, so they can better-understand what happened. This is only when mode is `commit` or `sync`, because `async` _means_ that the response is immediate, without waiting to see what happened to the transaction. [Pull request #2198](https://github.com/bigchaindb/bigchaindb/pull/2198)

### Known Issues

* If BigchainDB Server crashes and then is restarted, Tendermint Core won't try to reconnect to BigchainDB Server and so all operations requiring that connection won't work. We only understood this recently. We'll write a blog post explaining what we intend to do about it.
* The known issues in 2.0 Alpha (listed below) are still there.

## [2.0 Alpha] - 2018-04-03

Tag name: v2.0.0a1

There were _many_ changes between 1.3 and 2.0 Alpha, too many to list here. We wrote a series of blog posts to summarize most changes, especially those that affect end users and application developers:

* [BigchainDB 2.0 is Byzantine Fault Tolerant](https://blog.bigchaindb.com/bigchaindb-2-0-is-byzantine-fault-tolerant-5ffdac96bc44)
* [Some HTTP API Changes in the Next Release](https://blog.bigchaindb.com/some-http-api-changes-in-the-next-release-49612a537b0c)
* [Three Transaction Model Changes in the Next Release](https://blog.bigchaindb.com/three-transaction-model-changes-in-the-next-release-dadbac50094a)
* [Changes to the Server Command Line Interface in BigchainDB 2.0](https://blog.bigchaindb.com/changes-to-the-server-command-line-interface-in-bigchaindb-2-0-e1d6576e7155)
* _A forthcoming post about changes in BigchainDB Server configuration settings_

### External Contributors

* @r7vme contributed [pull request #1984](https://github.com/bigchaindb/bigchaindb/pull/1984) which fixed a bug in our Kubernetes-based production deployment template.

### Known Issues

We intend to resolve these issues before releasing the final BigchainDB 2.0:

* There's a known Heisenbug that (sometimes) arises and we found that making the BigchainDB webserver single-threaded prevents that bug from causing problems. We intend to resolve that bug, but in the meantime our temporary workaround is to change the _default_ webserver configuration settings to single-threaded mode, i.e. `BIGCHAINDB_SERVER_WORKERS=1` and `BIGCHAINDB_SERVER_THREADS=1`.
* Issues sometimes happen when a large transaction is sent to a BigchainDB network.

## [1.3] - 2017-11-21
Tag name: v1.3.0

### Added
* Metadata full-text search. [Pull request #1812](https://github.com/bigchaindb/bigchaindb/pull/1812)

### Notes
* Improved documentation about blocks and votes. [Pull request #1855](https://github.com/bigchaindb/bigchaindb/pull/1855)


## [1.2] - 2017-11-13
Tag name: v1.2.0

### Added
* New and improved installation setup docs and code. Pull requests [#1775](https://github.com/bigchaindb/bigchaindb/pull/1775) and [#1785](https://github.com/bigchaindb/bigchaindb/pull/1785)
* New BigchainDB configuration setting to set the port number of the log server: `log.port`. [Pull request #1796](https://github.com/bigchaindb/bigchaindb/pull/1796)
* New secondary index on `id` in the bigchain table. That will make some queries execute faster. [Pull request #1803](https://github.com/bigchaindb/bigchaindb/pull/1803)
* When using MongoDB, there are some restrictions on allowed names for keys (JSON keys). Those restrictions were always there but now BigchainDB checks key names explicitly, rather than leaving that to MongoDB. Pull requests [#1807](https://github.com/bigchaindb/bigchaindb/pull/1807) and [#1811](https://github.com/bigchaindb/bigchaindb/pull/1811)
* When using MongoDB, there are some restrictions on the allowed values of "language" (if that key is used in the values of `metadata` or `asset.data`). Those restrictions were always there but now BigchainDB checks the values explicitly, rather than leaving that to MongoDB. Pull requests [#1806](https://github.com/bigchaindb/bigchaindb/pull/1806) and [#1811](https://github.com/bigchaindb/bigchaindb/pull/1811)
* There's a new page in the root docs about permissions in BigchainDB. [Pull request #1788](https://github.com/bigchaindb/bigchaindb/pull/1788)
* There's a new option in the `bigchaindb start` command: `bigchaindb start --no-init` will avoid doing `bigchaindb init` if it wasn't done already. [Pull request #1814](https://github.com/bigchaindb/bigchaindb/pull/1814)

### Fixed
* Fixed a bug where setting the log level in a BigchainDB config file didn't have any effect. It does now. [Pull request #1797](https://github.com/bigchaindb/bigchaindb/pull/1797)
* The docs were wrong about there being no Ping/Pong support in the Events API. There is, so the docs were fixed. [Pull request #1799](https://github.com/bigchaindb/bigchaindb/pull/1799)
* Fixed an issue with closing WebSocket connections properly. [Pull request #1819](https://github.com/bigchaindb/bigchaindb/pull/1819)

### Notes
* Many changes were made to the Kubernetes-based production deployment template and code.


## [1.1] - 2017-09-26
Tag name: v1.1.0

### Added
* Support for server-side plugins that can add support for alternate event consumers (other than the WebSocket API). [Pull request #1707](https://github.com/bigchaindb/bigchaindb/pull/1707)
* New configuration settings to set the *advertised* wsserver scheme, host and port. (The *advertised* ones are the ones that external users use to connect to the WebSocket API.) [Pull request #1703](https://github.com/bigchaindb/bigchaindb/pull/1703)
* Support for secure (TLS) WebSocket connections. [Pull request #1619](https://github.com/bigchaindb/bigchaindb/pull/1619)
* A new page of documentation about the contents of a condition (inside a transaction). [Pull request #1668](https://github.com/bigchaindb/bigchaindb/pull/1668)

### Changed
* We updated our definition of the **public API** (at the top of this document). [Pull request #1700](https://github.com/bigchaindb/bigchaindb/pull/1700)
* The HTTP API Logger now logs the request path and method as well. [Pull request #1644](https://github.com/bigchaindb/bigchaindb/pull/1644)

### External Contributors
* @carchrae - [Pull request #1731](https://github.com/bigchaindb/bigchaindb/pull/1731)
* @ivanbakel - [Pull request #1706](https://github.com/bigchaindb/bigchaindb/pull/1706)
* @ketanbhatt - Pull requests [#1643](https://github.com/bigchaindb/bigchaindb/pull/1643) and [#1644](https://github.com/bigchaindb/bigchaindb/pull/1644)

### Notes
* New drivers & tools from our community:
    * [Java driver](https://github.com/authenteq/java-bigchaindb-driver), by [Authenteq](https://authenteq.com/)
    * [Ruby library](https://rubygems.org/gems/bigchaindb), by @nileshtrivedi
* Many improvements to our production deployment template (which uses Kubernetes).
* The production deployment template for the multi-node case was out of date. We updated that and verified it. [Pull request #1713](https://github.com/bigchaindb/bigchaindb/pull/1713)


## [1.0.1] - 2017-07-13
Tag name: v1.0.1

### Fixed
* Various issues in the Quickstart page. Pull requests
 [#1641](https://github.com/bigchaindb/bigchaindb/pull/1641) and
 [#1648](https://github.com/bigchaindb/bigchaindb/pull/1648).
* Changefeed hanging when MongoDB primary node is turned off.
 [Pull request #1638](https://github.com/bigchaindb/bigchaindb/pull/1638).
* Missing `assets` tables for RethinkDB backend.
 [Pull request #1646](https://github.com/bigchaindb/bigchaindb/pull/1646).
* Cryptoconditions version mismatch.
 [Pull request #1659](https://github.com/bigchaindb/bigchaindb/pull/1659).


## [1.0.0] - 2017-07-05
Tag name: v1.0.0

**This just reports the changes since the release of 1.0.0rc1. If you want the full picture of all changes since 0.10, then read the 1.0.0rc1 change log below as well as the upgrade guide.**

### Changed
* The file name of the upgrade guide changed from `docs/upgrade-guides/v0.10-->v1.0.md` to `docs/upgrade-guides/v0.10-v1.0.md`.
* In `transaction.inputs[n].fulfills`, `output` was renamed to `output_index`. [Pull Request #1596](https://github.com/bigchaindb/bigchaindb/pull/1596)
* In `transaction.outputs[n].condition.details`, 1) `signature` was removed (from signature conditions) and 2) `subfulfillments` was renamed to `subconditions` (in threshold conditions). [Pull Request #1589](https://github.com/bigchaindb/bigchaindb/pull/1589)
* Refined transaction schema validation to check that the `transaction.outputs[n].condition.uri` corresponds to a condition that BigchainDB Server 1.0.0 actually supports. [Pull Request #1597](https://github.com/bigchaindb/bigchaindb/pull/1597)
* Before, GET requests (to the HTTP API) with header `Content-Type: 'application/json'` would get a response with the message, "The browser (or proxy) sent a request that this server could not understand." Now, if a GET request includes a `Content-Type` header, that header gets deleted (i.e. ignored). [Pull Request #1630](https://github.com/bigchaindb/bigchaindb/pull/1630)

### Fixed
* If an end user sends a transaction with `operation` equal to `GENESIS`, it will be rejected as invalid. [Pull Request #1612](https://github.com/bigchaindb/bigchaindb/pull/1612)


## [1.0.0rc1] - 2017-06-23
Tag name: v1.0.0rc1

### Added
* Support for secure TLS/SSL communication between MongoDB and {BigchainDB, MongoDB Backup Agent, MongoDB Monitoring Agent}. Pull Requests
[#1456](https://github.com/bigchaindb/bigchaindb/pull/1456),
[#1497](https://github.com/bigchaindb/bigchaindb/pull/1497),
[#1510](https://github.com/bigchaindb/bigchaindb/pull/1510),
[#1536](https://github.com/bigchaindb/bigchaindb/pull/1536),
[#1551](https://github.com/bigchaindb/bigchaindb/pull/1551) and
[#1552](https://github.com/bigchaindb/bigchaindb/pull/1552).
* Text search support (only if using MongoDB). Pull Requests [#1469](https://github.com/bigchaindb/bigchaindb/pull/1469) and [#1471](https://github.com/bigchaindb/bigchaindb/pull/1471)
* The `database.connection_timeout` configuration setting now works with RethinkDB too. [#1512](https://github.com/bigchaindb/bigchaindb/pull/1512)
* New code and tools for benchmarking CREATE transactions. [Pull Request #1511](https://github.com/bigchaindb/bigchaindb/pull/1511)

### Changed
* There's an upgrade guide in `docs/upgrade-guides/v0.10-->v1.0.md`. It only covers changes to the transaction model and HTTP API. If that file hasn't been merged yet, see [Pull Request #1547](https://github.com/bigchaindb/bigchaindb/pull/1547)
* Cryptographic signatures now sign the whole (serialized) transaction body, including the transaction ID, but with all `"fulfillment"` values changed to `None`. [Pull Request #1225](https://github.com/bigchaindb/bigchaindb/pull/1225)
* In transactions, the value of `"amount"` must be a string. (Before, it was supposed to be a number.) [Pull Request #1286](https://github.com/bigchaindb/bigchaindb/pull/1286)
* In `setup.py`, the  "Development Status" (as reported on PyPI) was changed from Alpha to Beta. [Pull Request #1437](https://github.com/bigchaindb/bigchaindb/pull/1437)
* If you explicitly specify a config file, e.g. `bigchaindb -c path/to/config start` and that file can't be found, then BigchainDB Server will fail with a helpful error message. [Pull Request #1486](https://github.com/bigchaindb/bigchaindb/pull/1486)
* Reduced the response time on the HTTP API endpoint to get all the unspent outputs associated with a given public key (a.k.a. "fast unspents"). [Pull Request #1411](https://github.com/bigchaindb/bigchaindb/pull/1411)
* Internally, the value of an asset's `"data"` is now stored in a separate assets table. This enabled the new text search. Each asset data is stored along with the associated CREATE transaction ID (asset ID). That data gets written when the containing block gets written to the bigchain table. [Pull Request #1460](https://github.com/bigchaindb/bigchaindb/pull/1460)
* Schema validation was sped up by switching to `rapidjson-schema`. [Pull Request #1494](https://github.com/bigchaindb/bigchaindb/pull/1494)
* If a node comes back from being down for a while, it will resume voting on blocks in the order determined by the MongoDB oplog, in the case of MongoDB. (In the case of RethinkDB, blocks missed in the changefeed will not be voted on.) [Pull Request #1389](https://github.com/bigchaindb/bigchaindb/pull/1389)
* Parallelized transaction schema validation in the vote pipeline. [Pull Request #1492](https://github.com/bigchaindb/bigchaindb/pull/1492)
* `asset.data` or `asset.id` are now *required* in a CREATE or TRANSFER transaction, respectively. [Pull Request #1518](https://github.com/bigchaindb/bigchaindb/pull/1518)
* The HTTP response body, in the response to the `GET /` and the `GET /api/v1` endpoints, was changed substantially. [Pull Request #1529](https://github.com/bigchaindb/bigchaindb/pull/1529)
* Changed the HTTP `GET /api/v1/transactions/{transaction_id}` endpoint. It now only returns the transaction if it's in a valid block. It also returns a new header with a relative link to a status monitor. [Pull Request #1543](https://github.com/bigchaindb/bigchaindb/pull/1543)
* All instances of `txid` and `tx_id` were replaced with `transaction_id`, in the transaction model and the HTTP API. [Pull Request #1532](https://github.com/bigchaindb/bigchaindb/pull/1532)
* The hostname and port were removed from all URLs in all HTTP API responses. [Pull Request #1538](https://github.com/bigchaindb/bigchaindb/pull/1538)
* Relative links were replaced with JSON objects in HTTP API responses. [Pull Request #1541](https://github.com/bigchaindb/bigchaindb/pull/1541)
* In the outputs endpoint of the HTTP API, the query parameter `unspent` was changed to `spent` (so no more double negatives). If that query parameter isn't included, then all outputs matching the specificed public key will be returned. If `spent=true`, then only the spent outputs will be returned. If `spent=false`, then only the unspent outputs will be returned. [Pull Request #1545](https://github.com/bigchaindb/bigchaindb/pull/1545)
* The supported crypto-conditions changed from version 01 of the crypto-conditions spec to version 02. [Pull Request #1562](https://github.com/bigchaindb/bigchaindb/pull/1562)
* The value of "version" inside a transaction must now be "1.0". (Before, it could be "0.anything".) [Pull Request #1574](https://github.com/bigchaindb/bigchaindb/pull/1574)

### Removed
* The `server.threads` configuration setting (for the Gunicorn HTTP server) was removed from the default set of BigchainDB configuration settings. [Pull Request #1488](https://github.com/bigchaindb/bigchaindb/pull/1488)

### Fixed
* The `GET /api/v1/outputs` endpoint was failing for some transactions with threshold conditions. Fixed in [Pull Request #1450](https://github.com/bigchaindb/bigchaindb/pull/1450)

### External Contributors
* @elopio - Pull Requests [#1415](https://github.com/bigchaindb/bigchaindb/pull/1415) and [#1491](https://github.com/bigchaindb/bigchaindb/pull/1491)
* @CsterKuroi - [Pull Request #1447](https://github.com/bigchaindb/bigchaindb/pull/1447)
* @tdsgit - [Pull Request #1512](https://github.com/bigchaindb/bigchaindb/pull/1512)
* @lavinasachdev3 - [Pull Request #1357](https://github.com/bigchaindb/bigchaindb/pull/1357)

### Notes
* We dropped support for Python 3.4. [Pull Request #1564](https://github.com/bigchaindb/bigchaindb/pull/1564)
* There were many improvements to our Kubernetes-based production deployment template (and the associated documentaiton).
* There is now a [BigchainDB Ruby driver](https://github.com/LicenseRocks/bigchaindb_ruby), created by @addywaddy at [license.rocks](https://github.com/bigchaindb/bigchaindb/pull/1437).
* The [BigchainDB JavaScript driver](https://github.com/bigchaindb/js-bigchaindb-driver) was moved to a different GitHub repo and is now officially maintained by the BigchainDB team.
* We continue to recommend using MongoDB.

## [0.10.3] - 2017-06-29
Tag name: v0.10.3

## Fixed
* Pin minor+ version of `cryptoconditions` to avoid upgrading to a non
 compatible version.
[commit 97268a5](https://github.com/bigchaindb/bigchaindb/commit/97268a577bf27942a87d8eb838f4816165c84fd5)

## [0.10.2] - 2017-05-16
Tag name: v0.10.2

### Added
* Add Cross Origin Resource Sharing (CORS) support for the HTTP API.
 [Commit 6cb7596](https://github.com/bigchaindb/bigchaindb/commit/6cb75960b05403c77bdae0fd327612482589efcb)

### Fixed
* Fixed `streams_v1` API link in response to `GET /api/v1`.
 [Pull Request #1466](https://github.com/bigchaindb/bigchaindb/pull/1466)
* Fixed mismatch between docs and implementation for `GET /blocks?status=`
  endpoint. The `status` query parameter is now case insensitive.
 [Pull Request #1464](https://github.com/bigchaindb/bigchaindb/pull/1464)

## [0.10.1] - 2017-04-19
Tag name: v0.10.1

### Added
* Documentation for the BigchainDB settings `wsserver.host` and `wsserver.port`. [Pull Request #1408](https://github.com/bigchaindb/bigchaindb/pull/1408)

### Fixed
* Fixed `Dockerfile`, which was failing to build. It now starts `FROM python:3.6` (instead of `FROM ubuntu:xenial`). [Pull Request #1410](https://github.com/bigchaindb/bigchaindb/pull/1410)
* Fixed the `Makefile` so that `release` depends on `dist`. [Pull Request #1405](https://github.com/bigchaindb/bigchaindb/pull/1405)

## [0.10.0] - 2017-04-18
Tag name: v0.10.0

### Added
* Improved logging. Added logging to file. Added `--log-level` option to `bigchaindb start` command. Added new logging configuration settings. Pull Requests
[#1285](https://github.com/bigchaindb/bigchaindb/pull/1285),
[#1307](https://github.com/bigchaindb/bigchaindb/pull/1307),
[#1324](https://github.com/bigchaindb/bigchaindb/pull/1324),
[#1326](https://github.com/bigchaindb/bigchaindb/pull/1326),
[#1327](https://github.com/bigchaindb/bigchaindb/pull/1327),
[#1330](https://github.com/bigchaindb/bigchaindb/pull/1330),
[#1365](https://github.com/bigchaindb/bigchaindb/pull/1365),
[#1394](https://github.com/bigchaindb/bigchaindb/pull/1394),
[#1396](https://github.com/bigchaindb/bigchaindb/pull/1396),
[#1398](https://github.com/bigchaindb/bigchaindb/pull/1398) and
[#1402](https://github.com/bigchaindb/bigchaindb/pull/1402)
* Events API using WebSocket protocol. Pull Requests
[#1086](https://github.com/bigchaindb/bigchaindb/pull/1086),
[#1347](https://github.com/bigchaindb/bigchaindb/pull/1347),
[#1349](https://github.com/bigchaindb/bigchaindb/pull/1349),
[#1356](https://github.com/bigchaindb/bigchaindb/pull/1356),
[#1368](https://github.com/bigchaindb/bigchaindb/pull/1368),
[#1401](https://github.com/bigchaindb/bigchaindb/pull/1401) and
[#1403](https://github.com/bigchaindb/bigchaindb/pull/1403)
* Initial support for using SSL with MongoDB (work in progress). Pull Requests
[#1299](https://github.com/bigchaindb/bigchaindb/pull/1299) and
[#1348](https://github.com/bigchaindb/bigchaindb/pull/1348)

### Changed
* The main BigchainDB Dockerfile (and its generated Docker image) now contains only BigchainDB Server. (It used to contain both BigchainDB Server and RethinkDB.) You must now run MongoDB or RethinkDB in a separate Docker container. [Pull Request #1174](https://github.com/bigchaindb/bigchaindb/pull/1174)
* Made separate schemas for CREATE and TRANSFER transactions. [Pull Request #1257](https://github.com/bigchaindb/bigchaindb/pull/1257)
* When signing transactions with threshold conditions, we now sign all subconditions for a public key. [Pull Request #1294](https://github.com/bigchaindb/bigchaindb/pull/1294)
* Many changes to the voting-related code, including how we validate votes and prevent duplicate votes by the same node. Pull Requests [#1215](https://github.com/bigchaindb/bigchaindb/pull/1215) and [#1258](https://github.com/bigchaindb/bigchaindb/pull/1258)

### Removed
* Removed the `bigchaindb load` command. Pull Requests
[#1261](https://github.com/bigchaindb/bigchaindb/pull/1261),
[#1273](https://github.com/bigchaindb/bigchaindb/pull/1273) and
[#1301](https://github.com/bigchaindb/bigchaindb/pull/1301)
* Removed old `/speed-tests` and `/benchmarking-tests` directories. [Pull Request #1359](https://github.com/bigchaindb/bigchaindb/pull/1359)

### Fixed
* Fixed the URL of the BigchainDB docs returned by the HTTP API. [Pull Request #1178](https://github.com/bigchaindb/bigchaindb/pull/1178)
* Fixed the MongoDB changefeed: it wasn't reporting update operations. [Pull Request #1193](https://github.com/bigchaindb/bigchaindb/pull/1193)
* Fixed the block-creation process: it wasn't checking if the transaction was previously included in:
    * a valid block. [Pull Request #1208](https://github.com/bigchaindb/bigchaindb/pull/1208)
    * the block-under-construction. Pull Requests [#1237](https://github.com/bigchaindb/bigchaindb/issues/1237) and [#1377](https://github.com/bigchaindb/bigchaindb/issues/1377)

### External Contributors
In alphabetical order by GitHub username:
* @anryko - [Pull Request #1277](https://github.com/bigchaindb/bigchaindb/pull/1277)
* @anujism - [Pull Request #1366](https://github.com/bigchaindb/bigchaindb/pull/1366)
* @jackric - [Pull Request #1365](https://github.com/bigchaindb/bigchaindb/pull/1365)
* @lavinasachdev3 - [Pull Request #1358](https://github.com/bigchaindb/bigchaindb/pull/1358)
* @morrme - [Pull Request #1340](https://github.com/bigchaindb/bigchaindb/pull/1340)
* @tomconte - [Pull Request #1299](https://github.com/bigchaindb/bigchaindb/pull/1299)
* @tymlez - Pull Requests [#1108](https://github.com/bigchaindb/bigchaindb/pull/1108) & [#1209](https://github.com/bigchaindb/bigchaindb/pull/1209)

### Notes
* MongoDB is now the recommended database backend (not RethinkDB).
* There are some initial docs about how to deploy a BigchainDB node on Kubernetes. It's work in progress.


## [0.9.5] - 2017-03-29
Tag name: v0.9.5

### Fixed
Upgrade `python-rapidjson` to `0.0.11`(fixes #1350 - thanks to @ferOnti for
reporting).

## [0.9.4] - 2017-03-16
Tag name: v0.9.4

### Fixed
Fixed #1271 (false double spend error). Thanks to @jmduque for reporting the
problem along with a very detailed diagnosis and useful recommendations.

## [0.9.3] - 2017-03-06
Tag name: v0.9.3

### Fixed
Fixed HTTP API 500 error on `GET /outputs`: issues #1200 and #1231.

## [0.9.2] - 2017-03-02
Tag name: v0.9.2

### Fixed
Pin `python-rapidjson` library in `setup.py` to prevent `bigchaindb`'s
installation to fail due to
https://github.com/python-rapidjson/python-rapidjson/issues/62.

## [0.9.1] - 2017-02-06
Tag name: v0.9.1

### Fixed
* Fixed bug in how the transaction `VERSION` string was calculated from the BigchainDB Server `__short_version__` string. [Pull Request #1160](https://github.com/bigchaindb/bigchaindb/pull/1160)


## [0.9.0] - 2017-02-06
Tag name: v0.9.0

It has been more than two months since the v0.8.0 release, so there have been _many_ changes. We decided to describe them in broad strokes, with links to more details elsewhere.

### Added
- Support for MongoDB as a backend database.
- Some configuration settings and `bigchaindb` command-line commands were added. In particular, one can specify the database backend (`rethinkdb` or `mongodb`). For MongoDB, one can specify the name of the replicaset. Also for MongoDB, there are new command-line commands to add and remove hosts from the replicaset. See [the Settings & CLI docs](https://docs.bigchaindb.com/projects/server/en/v0.9.0/server-reference/index.html).
- Transaction schema validation. The transaction schema is also used to auto-generate some docs. [Pull Request #880](https://github.com/bigchaindb/bigchaindb/pull/880)
- Vote schema validation. The vote schema is also used to auto-generate some docs. [Pull Request #865](https://github.com/bigchaindb/bigchaindb/pull/865)
- New `ENABLE_WEB_ADMIN` setting in the AWS deployment configuration file. [Pull Request #1015](https://github.com/bigchaindb/bigchaindb/pull/1015)

### Changed
- The transaction model has changed substantially. @libscott wrote a blog post about the changes and it will be published soon on [the BigchainDB Blog](https://blog.bigchaindb.com/). Also, see [the docs about the transaction model](https://docs.bigchaindb.com/projects/server/en/v0.9.0/data-models/transaction-model.html).
- The HTTP API has changed substantially. @diminator wrote a blog post about the changes and it will be published soon on [the BigchainDB Blog](https://blog.bigchaindb.com/).  Also, see [the docs about the vote model](https://docs.bigchaindb.com/projects/server/en/v0.9.0/data-models/vote-model.html).
- All RethinkDB-specific database calls were replaced with abstract calls to a backend database.
- Some improvements to the Dockerfile, e.g. Pull Requests [#1011](https://github.com/bigchaindb/bigchaindb/pull/1011) and [#1121](https://github.com/bigchaindb/bigchaindb/pull/1121)
- Many improvements to the tests
- We standardized on supporting Ubuntu 16.04 for now (but BigchainDB Server also works on similar Linux distros).

### Removed
- `api_endpoint` was removed from the BigchainDB configuration settings. (It was never used anyway.) [Pull Request #821](https://github.com/bigchaindb/bigchaindb/pull/821)
- Removed all remaining StatsD monitoring code, configuration settings, docs, etc. (We'll add another monitoring solution in the future.) [Pull Request #1138](https://github.com/bigchaindb/bigchaindb/pull/1138)

### Fixed
- Fixed a memory (RAM) overflow problem when under heavy load by bounding the size of the queue at the entrance to the block pipeline. [Pull Request #908](https://github.com/bigchaindb/bigchaindb/pull/908)
- Fixed some logic in block validation. [Pull Request #1130](https://github.com/bigchaindb/bigchaindb/pull/1130)

### External Contributors
- @amirelemam - [Pull Request #762](https://github.com/bigchaindb/bigchaindb/pull/762) (closed but used as the basis for [Pull Request #1074](https://github.com/bigchaindb/bigchaindb/pull/1074))
- @utarl - [Pull Request #1019](https://github.com/bigchaindb/bigchaindb/pull/1019)

### Notes
- There were many additions and changes to the documentation. Fun fact: The JSON in the HTTP API docs is now auto-generated to be consistent with the current code.
- There's a draft spec for a BigchainDB Event Stream API and we welcome your feedback. See [Pull Request #1086](https://github.com/bigchaindb/bigchaindb/pull/1086)


## [0.8.2] - 2017-01-27
Tag name: v0.8.2

### Fixed
- Fix spend input twice in same transaction
  (https://github.com/bigchaindb/bigchaindb/issues/1099).


## [0.8.1] - 2017-01-16
Tag name: v0.8.1

### Changed
- Upgrade pysha3 to 1.0.0 (supports official NIST standard).

### Fixed
- Workaround for rapidjson problem with package metadata extraction
  (https://github.com/kenrobbins/python-rapidjson/pull/52).


## [0.8.0] - 2016-11-29
Tag name: v0.8.0

### Added
- The big new thing in version 0.8.0 is support for divisible assets, i.e. assets like carrots or thumbtacks, where the initial CREATE transaction can register/create some amount (e.g. 542 carrots), the first TRANSFER transaction can split that amount across multiple owners, and so on. [Pull Request #794](https://github.com/bigchaindb/bigchaindb/pull/794)
- Wrote a formal schema for the JSON structure of transactions. [Pull Request #798](https://github.com/bigchaindb/bigchaindb/pull/798)
- New configuration parameter: `backlog_reassign_delay`. [Pull Request #883](https://github.com/bigchaindb/bigchaindb/pull/883)

### Changed
- CREATE transactions must now be signed by all `owners_before` (rather than by a federation node). [Pull Request #794](https://github.com/bigchaindb/bigchaindb/pull/794)
- The user-provided timestamp was removed from the transaction data model (schema). [Pull Request #817](https://github.com/bigchaindb/bigchaindb/pull/817)
- `get_transaction()` will now return a transaction from the backlog, even if there are copies of the transaction in invalid blocks. [Pull Request #793](https://github.com/bigchaindb/bigchaindb/pull/793)
- Several pull requests to introduce a generalized database interface, to move RethinkDB calls into a separate implementation of that interface, and to work on a new MongoDB implementation of that interface. Pull Requests
[#754](https://github.com/bigchaindb/bigchaindb/pull/754),
[#783](https://github.com/bigchaindb/bigchaindb/pull/783),
[#799](https://github.com/bigchaindb/bigchaindb/pull/799),
[#806](https://github.com/bigchaindb/bigchaindb/pull/806),
[#809](https://github.com/bigchaindb/bigchaindb/pull/809),
[#853](https://github.com/bigchaindb/bigchaindb/pull/853)
- Renamed "verifying key" to "public key". Renamed "signing key" to "private key". Renamed "vk" to "pk". [Pull Request #807](https://github.com/bigchaindb/bigchaindb/pull/807)
- `get_transaction_by_asset_id` now ignores invalid transactions. [Pull Request #810](https://github.com/bigchaindb/bigchaindb/pull/810)
- `get_transaction_by_metadata_id` now ignores invalid transactions. [Pull Request #811](https://github.com/bigchaindb/bigchaindb/pull/811)
- Updates to the configs and scripts for deploying a test network on AWS. The example config file deploys virtual machines running Ubuntu 16.04 now. Pull Requests
[#771](https://github.com/bigchaindb/bigchaindb/pull/771),
[#813](https://github.com/bigchaindb/bigchaindb/pull/813)
- Changed logging of transactions on block creation so now it just says the length of the list of transactions, rather than listing all the transactions. [Pull Request #861](https://github.com/bigchaindb/bigchaindb/pull/861)

### Fixed
- Equality checks with AssetLinks. [Pull Request #825](https://github.com/bigchaindb/bigchaindb/pull/825)
- Bug in `bigchaindb load`. [Pull Request #824](https://github.com/bigchaindb/bigchaindb/pull/824)
- Two issues found with timestamp indexes. [Pull Request #816](https://github.com/bigchaindb/bigchaindb/pull/816)
- Hard-coded `backlog_reassign_delay`. [Pull Request #854](https://github.com/bigchaindb/bigchaindb/pull/854)
- Race condition in `test_stale_monitor.py`. [Pull Request #846](https://github.com/bigchaindb/bigchaindb/pull/846)
- When creating a signed vote, decode the vote signature to a `str`. [Pull Request #869](https://github.com/bigchaindb/bigchaindb/pull/869)
- Bug in AWS deployment scripts. Setting `BIND_HTTP_TO_LOCALHOST` to `False` didn't actually work. It does now. [Pull Request #870](https://github.com/bigchaindb/bigchaindb/pull/870)

### External Contributors
- @najlachamseddine - [Pull Request #528](https://github.com/bigchaindb/bigchaindb/pull/528)
- @ChristianGaertner - [Pull Request #659](https://github.com/bigchaindb/bigchaindb/pull/659)
- @MinchinWeb - [Pull Request #695](https://github.com/bigchaindb/bigchaindb/pull/695)
- @ckeyer - [Pull Request #785](https://github.com/bigchaindb/bigchaindb/pull/785)

### Notes
- @ChristianGaertner added a Python style checker (Flake8) to Travis CI, so external contributors should be aware that the Python code in their pull requests will be checked. See [our Python Style Guide](PYTHON_STYLE_GUIDE.md).
- Several additions and changes to the documentation, e.g. Pull Requests
[#690](https://github.com/bigchaindb/bigchaindb/pull/690),
[#764](https://github.com/bigchaindb/bigchaindb/pull/764),
[#766](https://github.com/bigchaindb/bigchaindb/pull/766),
[#769](https://github.com/bigchaindb/bigchaindb/pull/769),
[#777](https://github.com/bigchaindb/bigchaindb/pull/777),
[#800](https://github.com/bigchaindb/bigchaindb/pull/800),
[#801](https://github.com/bigchaindb/bigchaindb/pull/801),
[#802](https://github.com/bigchaindb/bigchaindb/pull/802),
[#803](https://github.com/bigchaindb/bigchaindb/pull/803),
[#819](https://github.com/bigchaindb/bigchaindb/pull/819),
[#827](https://github.com/bigchaindb/bigchaindb/pull/827),
[#859](https://github.com/bigchaindb/bigchaindb/pull/859),
[#872](https://github.com/bigchaindb/bigchaindb/pull/872),
[#882](https://github.com/bigchaindb/bigchaindb/pull/882),
[#883](https://github.com/bigchaindb/bigchaindb/pull/883)


## [0.7.0] - 2016-10-28
Tag name: v0.7.0
= commit: 2dd7f1af27478c529e6d2d916f64daa3fbda3885
committed: Oct 28, 2016, 4:00 PM GMT+2

### Added
- Stale transactions in the `backlog` table now get reassigned to another node (for inclusion in a new block): [Pull Request #359](https://github.com/bigchaindb/bigchaindb/pull/359)
- Many improvements to make the database connection more robust: [Pull Request #623](https://github.com/bigchaindb/bigchaindb/pull/623)
- The new `--dev-allow-temp-keypair` option on `bigchaindb start` will generate a temporary keypair if no keypair is found. The `Dockerfile` was updated to use this. [Pull Request #635](https://github.com/bigchaindb/bigchaindb/pull/635)
- The AWS deployment scripts now allow you to:
   - specify the AWS security group as a configuration parameter: [Pull Request #620](https://github.com/bigchaindb/bigchaindb/pull/620)
   - tell RethinkDB to bind HTTP to localhost (a more secure setup; now the default in the example config file): [Pull Request #666](https://github.com/bigchaindb/bigchaindb/pull/666)

### Changed
- Integrated the new `Transaction` model. This was a **big** change; 49 files changed. [Pull Request #641](https://github.com/bigchaindb/bigchaindb/pull/641)
- Merged "common" code (used by BigchainDB Server and the Python driver), which used to be in its own repository (`bigchaindb/bigchaindb-common`), into the main `bigchaindb/bigchaindb` repository (this one): [Pull Request #742](https://github.com/bigchaindb/bigchaindb/pull/742)
- Integrated the new digital asset model. This changed the data structure of a transaction and will make it easier to support divisible assets in the future. [Pull Request #680](https://github.com/bigchaindb/bigchaindb/pull/680)
- Transactions are now deleted from the `backlog` table _after_ a block containing them is written to the `bigchain` table: [Pull Request #609](https://github.com/bigchaindb/bigchaindb/pull/609)
- Changed the example AWS deployment configuration file: [Pull Request #665](https://github.com/bigchaindb/bigchaindb/pull/665)
- Support for version 0.5.0 of the `cryptoconditions` Python package. Note that this means you must now install `ffi.h` (e.g. `sudo apt-get install libffi-dev` on Ubuntu). See Pull Requests [#685](https://github.com/bigchaindb/bigchaindb/pull/685) and [#698](https://github.com/bigchaindb/bigchaindb/pull/698)
- Updated some database access code: Pull Requests [#676](https://github.com/bigchaindb/bigchaindb/pull/676) and [#701](https://github.com/bigchaindb/bigchaindb/pull/701)

### Fixed
- Internally, when a transaction is in the `backlog` table, it carries some extra book-keeping fields:
   1. an `assignment_timestamp` (i.e. the time when it was assigned to a node), which is used to determine if it has gone stale.
   2. an `assignee`: the public key of the node it was assigned to.
- The `assignment_timestamp` wasn't removed before writing the transaction to a block. That was fixed in [Pull Request #627](https://github.com/bigchaindb/bigchaindb/pull/627)
- The `assignment_timestamp` and `assignee` weren't removed in the response to an HTTP API request sent to the `/api/v1/transactions/<txid>` endpoint. That was fixed in [Pull Request #646](https://github.com/bigchaindb/bigchaindb/pull/646)
- When validating a TRANSFER transaction, if any fulfillment refers to a transaction that's _not_ in a valid block, then the transaction isn't valid. This wasn't checked before but it is now. [Pull Request #629](https://github.com/bigchaindb/bigchaindb/pull/629)

### External Contributors
- @MinchinWeb - [Pull Request #696](https://github.com/bigchaindb/bigchaindb/pull/696)

### Notes
- We made a small change to how we do version labeling. Going forward, we will have the version label set to 0.X.Y.dev in the master branch as we work on what will eventually be released as version 0.X.Y. The version number will only be changed to 0.X.Y just before the release. This version labeling scheme began with [Pull Request #752](https://github.com/bigchaindb/bigchaindb/pull/752)
- Several additions and changes to the documentation, e.g. Pull Requests
[#618](https://github.com/bigchaindb/bigchaindb/pull/618),
[#621](https://github.com/bigchaindb/bigchaindb/pull/621),
[#625](https://github.com/bigchaindb/bigchaindb/pull/625),
[#645](https://github.com/bigchaindb/bigchaindb/pull/645),
[#647](https://github.com/bigchaindb/bigchaindb/pull/647),
[#648](https://github.com/bigchaindb/bigchaindb/pull/648),
[#650](https://github.com/bigchaindb/bigchaindb/pull/650),
[#651](https://github.com/bigchaindb/bigchaindb/pull/651),
[#653](https://github.com/bigchaindb/bigchaindb/pull/653),
[#655](https://github.com/bigchaindb/bigchaindb/pull/655),
[#656](https://github.com/bigchaindb/bigchaindb/pull/656),
[#657](https://github.com/bigchaindb/bigchaindb/pull/657),
[#667](https://github.com/bigchaindb/bigchaindb/pull/667),
[#668](https://github.com/bigchaindb/bigchaindb/pull/668),
[#669](https://github.com/bigchaindb/bigchaindb/pull/669),
[#673](https://github.com/bigchaindb/bigchaindb/pull/673),
[#678](https://github.com/bigchaindb/bigchaindb/pull/678),
[#684](https://github.com/bigchaindb/bigchaindb/pull/684),
[#688](https://github.com/bigchaindb/bigchaindb/pull/688),
[#699](https://github.com/bigchaindb/bigchaindb/pull/699),
[#705](https://github.com/bigchaindb/bigchaindb/pull/705),
[#737](https://github.com/bigchaindb/bigchaindb/pull/737),
[#748](https://github.com/bigchaindb/bigchaindb/pull/748),
[#753](https://github.com/bigchaindb/bigchaindb/pull/753),
[#757](https://github.com/bigchaindb/bigchaindb/pull/757),
[#759](https://github.com/bigchaindb/bigchaindb/pull/759), and more


## [0.6.0] - 2016-09-01
Tag name: v0.6.0
= commit: bfc86e0295c7d1ef0acd3c275c125798bd5b0dfd
committed: Sep 1, 2016, 2:15 PM GMT+2

### Added
- Support for multiple operations in the ChangeFeed class: [Pull Request #569](https://github.com/bigchaindb/bigchaindb/pull/569)
- Instructions, templates and code for deploying a starter node on AWS using Terraform and Ansible: Pull Requests
[#572](https://github.com/bigchaindb/bigchaindb/pull/572),
[#589](https://github.com/bigchaindb/bigchaindb/pull/589),
[#600](https://github.com/bigchaindb/bigchaindb/pull/600),
[#605](https://github.com/bigchaindb/bigchaindb/pull/605),
[#610](https://github.com/bigchaindb/bigchaindb/pull/610)
- Check that the majority of votes on a block agree on the previous block. If they don't, consider the block invalid. [Pull Request #565](https://github.com/bigchaindb/bigchaindb/pull/565)

### Changed
- Set RethinkDB `read-mode='majority'` everywhere: [Pull Request #497](https://github.com/bigchaindb/bigchaindb/pull/497)
- Ported election logic and voting logic to the new pipeline architecture: Pull Requests [#510](https://github.com/bigchaindb/bigchaindb/pull/510) and [#515](https://github.com/bigchaindb/bigchaindb/pull/515)
- Moved the transaction (model) `version` inside the `transaction` (in the transaction data model): [Pull Request #518](https://github.com/bigchaindb/bigchaindb/pull/518)
- Changed how the BigchainDB config file (JSON) gets written so it's easier for humans to read: [Pull Request #522](https://github.com/bigchaindb/bigchaindb/pull/522)
- Improved and expanded the GET/POST endpoints for transactions (in the HTTP API): [Pull Request #563](https://github.com/bigchaindb/bigchaindb/pull/563)
- Changed the AWS cluster deployment scripts so that the deployer now generates their keypair locally, rather than having Amazon do it: [Pull Request #567](https://github.com/bigchaindb/bigchaindb/pull/567)
- When a transaction is retrieved by `get_transaction`, a `validity` field is added with a value one of `valid`, `undecided`, or `backlog`: [Pull Request #574](https://github.com/bigchaindb/bigchaindb/pull/574)
- Renamed `current_owners` and `new_owners` (in the data models) to `owners_before` and `owners_after`, respectively (i.e. before/after *the transaction*): [Pull Request #578](https://github.com/bigchaindb/bigchaindb/pull/578)
- Use `flask_restful` and class-based views for realizing the HTTP API: [Pull Request #588](https://github.com/bigchaindb/bigchaindb/pull/588)

### Fixed
- Fixed the confusing error message when there was a syntax error in the BigchainDB config file: [Pull Request #531](https://github.com/bigchaindb/bigchaindb/pull/531)
- Fixed `write_transaction` so it no longer has the side effect of adding `assignee` to a transaction that is being processed: [Pull Request #606](https://github.com/bigchaindb/bigchaindb/pull/606)

### External Contributors
- @eladve - [Pull Request #518](https://github.com/bigchaindb/bigchaindb/pull/518)
- @d01phin - Pull Requests [#522](https://github.com/bigchaindb/bigchaindb/pull/522) and [#531](https://github.com/bigchaindb/bigchaindb/pull/531)
- @Kentoseth - [Pull Request #537](https://github.com/bigchaindb/bigchaindb/pull/537)

### Notes
- Several additions and changes to the documentation, e.g. Pull Requests
[#523](https://github.com/bigchaindb/bigchaindb/pull/523),
[#532](https://github.com/bigchaindb/bigchaindb/pull/532),
[#537](https://github.com/bigchaindb/bigchaindb/pull/537),
[#539](https://github.com/bigchaindb/bigchaindb/pull/539),
[#610](https://github.com/bigchaindb/bigchaindb/pull/610), and more


## [0.5.1] - 2016-07-29
Tag name: v0.5.1
= commit: ff042b5954abe48c7264d43128d52584eab2a806
committed: Jul 29, 2016, 2:38 PM GMT+2

### Added
- New third table, the 'votes' table: [Pull Request #379](https://github.com/bigchaindb/bigchaindb/pull/379)
- Added `get_tx_by_payload_uuid()` including index: [Pull Request #411](https://github.com/bigchaindb/bigchaindb/pull/411)
- Ability to deploy a test cluster on AWS using Amazon Elastic Block Store (EBS) for storage: [Pull Request #469](https://github.com/bigchaindb/bigchaindb/pull/469)
- Ability to add different-size payloads to transactions when filling the backlog for benchmarking: [Pull Request #273](https://github.com/bigchaindb/bigchaindb/pull/273)

### Changed
- Votes are no longer appended to the blocks inside the 'bigchain' table. They're now written to their own table, the 'votes' table: [Pull Request #379](https://github.com/bigchaindb/bigchaindb/pull/379)
- Refactored how blocks get constructed using the new approach to doing multiprocessing, using the `multipipes` package: [Pull Request #484](https://github.com/bigchaindb/bigchaindb/pull/484)
- Changed all queries to use `read_mode='majority'`: [Pull Request #497](https://github.com/bigchaindb/bigchaindb/pull/497)
- Revised how base software gets deployed on AWS instances: [Pull Request #478](https://github.com/bigchaindb/bigchaindb/pull/478)
- Refactored `db.utils.init()`: [Pull Request #471](https://github.com/bigchaindb/bigchaindb/pull/471)

### External Contributors
- @shauns - [Pull Request #411](https://github.com/bigchaindb/bigchaindb/pull/411)
- @lonelypeanut - [Pull Request #479](https://github.com/bigchaindb/bigchaindb/pull/479)
- @lluminita - Pull Requests [#435](https://github.com/bigchaindb/bigchaindb/pull/435) & [#471](https://github.com/bigchaindb/bigchaindb/pull/471)

### Notes
- Several additions and changes to the documentation: Pull Requests
[#416](https://github.com/bigchaindb/bigchaindb/pull/416),
[#417](https://github.com/bigchaindb/bigchaindb/pull/417),
[#418](https://github.com/bigchaindb/bigchaindb/pull/418),
[#420](https://github.com/bigchaindb/bigchaindb/pull/420),
[#421](https://github.com/bigchaindb/bigchaindb/pull/421),
[#422](https://github.com/bigchaindb/bigchaindb/pull/422),
[#423](https://github.com/bigchaindb/bigchaindb/pull/423),
[#425](https://github.com/bigchaindb/bigchaindb/pull/425),
[#428](https://github.com/bigchaindb/bigchaindb/pull/428),
[#430](https://github.com/bigchaindb/bigchaindb/pull/430),
[#431](https://github.com/bigchaindb/bigchaindb/pull/431),
[#435](https://github.com/bigchaindb/bigchaindb/pull/435),
[#442](https://github.com/bigchaindb/bigchaindb/pull/442),
[#472](https://github.com/bigchaindb/bigchaindb/pull/472),
[#481](https://github.com/bigchaindb/bigchaindb/pull/481)


## [0.5.0] - 2016-07-04
Tag name: v0.5.0
= commit: 38329531304952128b48f2e5603db5fa08069c26
committed: July 4, 2016, 1:07 PM GMT+2

### Added
- New `bigchaindb set-replicas` subcommand: [Pull Request #392](https://github.com/bigchaindb/bigchaindb/pull/392)
- Informative JSON message when one makes a request to the root endpoint of the HTTP client-server API: [Pull Request #367](https://github.com/bigchaindb/bigchaindb/pull/367)
- Return HTTP response code 404 when a transaction is not found: [Pull Request #369](https://github.com/bigchaindb/bigchaindb/pull/369)

### Changed
- Changed the order in which configuration settings get their values. If a setting is set by an environment variable, then that value will be _the_ value, regardless of whether another value is set in a local config file. Also added a method to programattically update the config settings. [Pull Request #395](https://github.com/bigchaindb/bigchaindb/pull/395)
- Changed the definition of `util.sign_tx()`. It now has a third, optional argument: a Bigchain instance. [Pull Request #410](https://github.com/bigchaindb/bigchaindb/pull/410)

### Notes
- Several additions and changes to the documentation: Pull Requests
[#388](https://github.com/bigchaindb/bigchaindb/pull/388),
[#393](https://github.com/bigchaindb/bigchaindb/pull/393),
[#397](https://github.com/bigchaindb/bigchaindb/pull/397),
[#402](https://github.com/bigchaindb/bigchaindb/pull/402),
[#403](https://github.com/bigchaindb/bigchaindb/pull/403),
[#406](https://github.com/bigchaindb/bigchaindb/pull/406),
[#408](https://github.com/bigchaindb/bigchaindb/pull/408)


## [0.4.2] - 2016-06-15
Tag name: v0.4.2
= commit: 7ce6c3980cf70437d7ce716a67f069afa8ecb79e
committed: June 15, 2016, 1:42 PM GMT+2

### Added
- Report the BigchainDB version number when starting BigchainDB: [Pull Request #385](https://github.com/bigchaindb/bigchaindb/pull/385)

### Changed
- Round timestamps to a precision of one second, and replace payload hash with payload UUID in transactions: [Pull Request #384](https://github.com/bigchaindb/bigchaindb/pull/384)
- Updated cryptoconditions API usage: [Pull Request #373](https://github.com/bigchaindb/bigchaindb/pull/373)


## [0.4.1] - 2016-06-13
Tag name: v0.4.1
= commit: 9c4aa987bcbc294b6a5c3069e6c45a7ed77a4068
committed: June 13, 2016, 9:52 AM GMT+2

### Added
- Revert `bigchain` deletes: [Pull Request #330](https://github.com/bigchaindb/bigchaindb/pull/330)

### Changed
- Use inverted threshold condition instead of negative weights for escrow: [Pull Request #355](https://github.com/bigchaindb/bigchaindb/pull/355)

### Fixed
- Removed duplicate `pytest` in `setup.py`: [Pull Request #365](https://github.com/bigchaindb/bigchaindb/pull/365)

### Notes
- There were several additions and changes to the documentation: Pull Requests
[#343](https://github.com/bigchaindb/bigchaindb/pull/343),
[#363](https://github.com/bigchaindb/bigchaindb/pull/363),
[#364](https://github.com/bigchaindb/bigchaindb/pull/364),
[#366](https://github.com/bigchaindb/bigchaindb/pull/366),
[#370](https://github.com/bigchaindb/bigchaindb/pull/370),
[#372](https://github.com/bigchaindb/bigchaindb/pull/372)


## [0.4.0] - 2016-05-27
Tag name: v0.4.0
= commit: a89399c4f9fcdf82df73e0d8191af9e539d8d081
committed: May 27, 2016, 1:42 PM GMT+2

### Added
- Support for escrow (possible because of two other new things: cryptoconditions with inverters, and a timeout condition): [Pull Request #329](https://github.com/bigchaindb/bigchaindb/pull/329)
- Caching of calls to `load_consensus_plugin()`, using [`@lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache). This speeds up the instantiation of `Bigchain` objects and greatly improves overall performance. [Pull Request #271](https://github.com/bigchaindb/bigchaindb/pull/271)
- New `Dockerfile-dev` Docker file to make it easier for developers to _develop_ BigchainDB with Docker. One can run all unit tests with Docker again. [Pull Request #313](https://github.com/bigchaindb/bigchaindb/pull/313)
- Transactions in invalid blocks are copied to the backlog: [Pull Request #221](https://github.com/bigchaindb/bigchaindb/pull/221).
- Queries to the bigchain table now ignore invalid blocks: [Pull Request #324](https://github.com/bigchaindb/bigchaindb/issues/324)
- Use secondary index on get_transaction: [Pull Request #324](https://github.com/bigchaindb/bigchaindb/issues/324)
- New `bigchaindb` command to set the number of RethinkDB shards (in both tables): [Pull Request #258](https://github.com/bigchaindb/bigchaindb/pull/258)
- Better handling of an outdated `setuptools`: [Pull Request #279](https://github.com/bigchaindb/bigchaindb/pull/279)

### Changed
- The block processes now use GroupProcess: [Pull Request #267](https://github.com/bigchaindb/bigchaindb/pull/267)
- Replaced the `json` Python package with `rapidjson` (a Python wrapper for a fast JSON parser/generator written in C++), to speed up JSON serialization and deserialization: [Pull Request #318](https://github.com/bigchaindb/bigchaindb/pull/318)
- Overhauled `ROADMAP.md` and moved it to [the bigchaindb/org repository](https://github.com/bigchaindb/org): Pull Requests
[#282](https://github.com/bigchaindb/bigchaindb/pull/282),
[#306](https://github.com/bigchaindb/bigchaindb/pull/306),
[#308](https://github.com/bigchaindb/bigchaindb/pull/308),
[#325](https://github.com/bigchaindb/bigchaindb/pull/325)
- AWS deployment has better support for [New Relic Server Monitoring](https://newrelic.com/server-monitoring): [Pull Request #316](https://github.com/bigchaindb/bigchaindb/pull/316)
- AWS deployment script now reads from a configuration file: [Pull Request #291](https://github.com/bigchaindb/bigchaindb/pull/291)
- AWS deployment script doesn't auto-start the BigchainDB servers anymore: [Pull Request #257](https://github.com/bigchaindb/bigchaindb/pull/257)

### Fixed
- Bug related to transaction malleability: [Pull Request #281](https://github.com/bigchaindb/bigchaindb/pull/281)

### Notes
You can now see a big-picture view of all BigchainDB repositories on [a waffle.io board](https://waffle.io/bigchaindb/org).


## [0.3.0] - 2016-05-03
Tag name: v0.3.0
= commit: a97c54e82be954a1411e5bfe0f09a9c631309f1e
committed: May 3, 2016, 11:52 AM GMT+2

### Added
- Crypto-conditions specs according to the Interledger protocol: [Pull Request #174](https://github.com/bigchaindb/bigchaindb/pull/174)
- Added support for anonymous hashlocked conditions and fulfillments: [Pull Request #211](https://github.com/bigchaindb/bigchaindb/pull/211)

### Changed
- Several improvements to the AWS deployment scripts: [Pull Request #227](https://github.com/bigchaindb/bigchaindb/pull/227)

### Fixed
- Bug related to block validation: [Pull Request #233](https://github.com/bigchaindb/bigchaindb/pull/233)

### Notes
This release completely refactored the structure of the transactions and broke compatibility with older versions
of BigchainDB. The refactor of the transactions was made in order to add support for multiple inputs/outputs and
the crypto-conditions specs from the Interledger protocol.

We also updated the RethinkDB Python drivers so you need to upgrade to RethinkDB v2.3+


## [0.2.0] - 2016-04-26
Tag name: v0.2.0
= commit: 0c4a2b380aabdcf50fa2d7fb351c290aaedc3db7
committed: April 26, 2016, 11:09 AM GMT+2

### Added
- Ability to use environment variables to set (or partially set) configuration settings: [Pull Request #153](https://github.com/bigchaindb/bigchaindb/pull/153)
- `bigchaindb --export-my-pubkey`: [Pull Request #186](https://github.com/bigchaindb/bigchaindb/pull/186)
- `bigchaindb --version`, and one central source for the current version (`version.py`): [Pull Request #208](https://github.com/bigchaindb/bigchaindb/pull/208)
- AWS deployment scripts: Pull Requests
[#160](https://github.com/bigchaindb/bigchaindb/pull/160),
[#166](https://github.com/bigchaindb/bigchaindb/pull/166),
[#172](https://github.com/bigchaindb/bigchaindb/pull/172),
[#203](https://github.com/bigchaindb/bigchaindb/pull/203)
- `codecov.yml`: [Pull Request #161](https://github.com/bigchaindb/bigchaindb/pull/161)
- `CHANGELOG.md` (this file): [Pull Request #117](https://github.com/bigchaindb/bigchaindb/pull/117)
- Signatures using Ed25519: Pull Requests
[#138](https://github.com/bigchaindb/bigchaindb/pull/138),
[#152](https://github.com/bigchaindb/bigchaindb/pull/152)
- Multisig support: [Pull Request #107](https://github.com/bigchaindb/bigchaindb/pull/107)
- HTTP Server & Web API: Pull Requests
[#102](https://github.com/bigchaindb/bigchaindb/pull/102),
[#150](https://github.com/bigchaindb/bigchaindb/pull/150),
[#155](https://github.com/bigchaindb/bigchaindb/pull/155),
[#183](https://github.com/bigchaindb/bigchaindb/pull/183)
- Python driver/SDK/API: [Pull Request #102](https://github.com/bigchaindb/bigchaindb/pull/102)
- Python Style Guide: [Pull Request #89](https://github.com/bigchaindb/bigchaindb/pull/89)
- Monitoring & dashboard tools: Pull Requests
[#72](https://github.com/bigchaindb/bigchaindb/pull/72),
[#181](https://github.com/bigchaindb/bigchaindb/pull/181)

### Changed
- Rewrote [`README.md`](README.md) into four sets of links: Pull Requests [#80](https://github.com/bigchaindb/bigchaindb/pull/80) and [#115](https://github.com/bigchaindb/bigchaindb/pull/115)

### Fixed
- Bug related to config overwrite: [Pull Request #97](https://github.com/bigchaindb/bigchaindb/pull/97)
- Bug related to running the `bigchaindb-benchmark load` on docker [Pull Request #225](https://github.com/bigchaindb/bigchaindb/pull/225)

## External Contributors
- [@thedoctor](https://github.com/thedoctor): Pull Requests
[#99](https://github.com/bigchaindb/bigchaindb/pull/99),
[#136](https://github.com/bigchaindb/bigchaindb/pull/136)
- [@roderik](https://github.com/roderik): [Pull Request #162](https://github.com/bigchaindb/bigchaindb/pull/162)


## [0.1.5] - 2016-04-20
Tag name: v0.1.5
= commit: 9f62cddbaf44167692cfee71db707bce93e3395f
committed: April 20, 2016, 3:31 PM GMT+2

### Fixed
- [Issue #71](https://github.com/bigchaindb/bigchaindb/issues/71) (Voter is not validating blocks correctly when checking for double spends) in [Pull Request #76](https://github.com/bigchaindb/bigchaindb/pull/76)


## [0.1.4] - 2016-02-22
Tag name: v0.1.4
= commit: c4c850f480bc9ae72df2a54f81c0825b6fb4ed62
committed: Feb 22, 2016, 11:51 AM GMT+1

### Added
- Added to `classifiers` to setup.py

### Changed
- Allow running pytest tests in parallel (using [xdist](http://pytest.org/latest/xdist.html)): [Pull Request #65](https://github.com/bigchaindb/bigchaindb/pull/65)
- Allow non-interactive first start: [Pull Request #64](https://github.com/bigchaindb/bigchaindb/pull/64) to resolve [Issue #58](https://github.com/bigchaindb/bigchaindb/issues/58)


## [0.1.3] - 2016-02-16
Tag name: v0.1.3
= commit 8926e3216c1ee39b9bc332e5ef1df2a8901262dd
committed Feb 16, 2016, 11:37 AM GMT+1

### Changed
- Changed from using Git Flow to GitHub flow (but with `develop` as the default branch).


## [0.1.2] - 2016-02-15
Tag name: v0.1.2
= commit d2ff24166d69dda68dd7b4a24a88279b1d37e222
committed Feb 15, 2016, 2:23 PM GMT+1

### Added
- Various tests

### Fixed
- Fix exception when running `start`: [Pull Request #32](https://github.com/bigchaindb/bigchaindb/pull/32) resolved [Issue #35]

## [0.1.1] - 2016-02-15
Tag name: v0.1.1
= commit 2a025448b29fe7056760de1039c73bbcfe992461
committed Feb 15, 2016, 10:48 AM GMT+1

### Added
- "release 0.1.1": [Pull Request #37](https://github.com/bigchaindb/bigchaindb/pull/37)

### Removed
- `tox.ini` [Pull Request #18](https://github.com/bigchaindb/bigchaindb/pull/18)
- `requirements.txt` in the root directory, and the entire `requirements/` directory: [Pull Request #14](https://github.com/bigchaindb/bigchaindb/pull/14)

### Fixed
- Hotfix for AttributeError, fixed [Issue #27](https://github.com/bigchaindb/bigchaindb/issues/27)


## [0.1.0] - 2016-02-10
Tag name: v0.1.0
= commit 8539e8dc2d036a4e0a866a3fb9e55889503254d5
committed Feb 10, 2016, 10:04 PM GMT+1

The first public release of BigchainDB, including:

- Initial BigchainDB Server code, including many tests and some code for benchmarking.
- Initial documentation (in `bigchaindb/docs`).
- Initial `README.md`, `ROADMAP.md`, `CODE_OF_CONDUCT.md`, and `CONTRIBUTING.md`.
- Packaging for PyPI, including `setup.py` and `setup.cfg`.
- Initial `Dockerfile` and `docker-compose.yml` (for deployment using Docker and Docker Compose).
- Initial `.gitignore` (list of things for git to ignore).
- Initial `.travis.yml` (used by Travis CI).
