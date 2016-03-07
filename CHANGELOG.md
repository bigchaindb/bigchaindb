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


## [Unreleased] - YYYY-MM-DD
Tag name: TBD
= commit: TBD
committed: TBD

### Added
- `CHANGELOG.md` (this file)
- Multisig support: [Pull Request #107](https://github.com/bigchaindb/bigchaindb/pull/107).
- API/Wire protocol (RESTful HTTP API): [Pull Request #102](https://github.com/bigchaindb/bigchaindb/pull/102).
- Python driver/SDK/API: [Pull Request #102](https://github.com/bigchaindb/bigchaindb/pull/102).
- Python Style Guide: [Pull Request #89](https://github.com/bigchaindb/bigchaindb/pull/89)
- Monitoring & dashboard tools: [Pull Request #72](https://github.com/bigchaindb/bigchaindb/pull/72).

### Changed
- Rewrote [`README.md`](https://github.com/bigchaindb/bigchaindb/blob/develop/README.md) into four sets of links: Pull Requests [#80](https://github.com/bigchaindb/bigchaindb/pull/80) and [#115](https://github.com/bigchaindb/bigchaindb/pull/115)

### Fixed
- Bug related to config overwrite: [Pull Request #97](https://github.com/bigchaindb/bigchaindb/pull/97)
- [Issue #71](https://github.com/bigchaindb/bigchaindb/issues/71) (Voter is not validating blocks correctly when checking for double spends) in [Pull Request #76](https://github.com/bigchaindb/bigchaindb/pull/76)


## [0.1.4] - 2016-02-22
Tag name: v0.1.4 
= commit: c4c850f480bc9ae72df2a54f81c0825b6fb4ed62 
committed: Feb 22, 2016, 11:51 AM GMT+1

### Added
- Add classifiers

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


## [0.1.1] - 2016-02-15
Tag name: v0.1.1 
= commit 2a025448b29fe7056760de1039c73bbcfe992461 
committed Feb 15, 2016, 10:48 AM GMT+1

### Added
- "release 0.1.1": [Pull Request #37](https://github.com/bigchaindb/bigchaindb/pull/37)

### Removed
- `tox.ini` [Pull Request #18](https://github.com/bigchaindb/bigchaindb/pull/18)
- `requirements.txt` in the root directory, and the entire `requirements/` directory: [Pull Request #14](https://github.com/bigchaindb/bigchaindb/pull/14)


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
