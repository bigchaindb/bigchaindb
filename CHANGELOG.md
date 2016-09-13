# Change Log (Release Notes)
All _notable_ changes to this project will be documented in this file (`CHANGELOG.md`).
This project adheres to [Semantic Versioning](http://semver.org/) (or at least we try).
Contributors to this file, please follow the guidelines on [keepachangelog.com](http://keepachangelog.com/).
Note that each version (or "release") is the name of a [Git _tag_](https://git-scm.com/book/en/v2/Git-Basics-Tagging) of a particular commit, so the associated date and time are the date and time of that commit (as reported by GitHub), _not_ the "Uploaded on" date listed on PyPI (which may differ).
For reference, the possible headings are:

* **Added** for new features.
* **Changed** for changes in existing functionality.
* **Deprecated** for once-stable features removed in upcoming releases.
* **Removed** for deprecated features removed in this release.
* **Fixed** for any bug fixes.
* **Security** to invite users to upgrade in case of vulnerabilities.
* **External Contributors** to list contributors outside of BigchainDB GmbH.
* **Notes**


## [0.6.0] - 2016-09-01
Tag name: v0.6.0
= commit: 
committed: 

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
