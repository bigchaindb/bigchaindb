# Our Release Process

This is a summary of the steps we go through to release a new version of BigchainDB Server.

1. Update the `CHANGELOG.md` file
2. Update `bigchaindb/version.py`
3. Go to the [bigchaindb/bigchaindb Releases page on GitHub](https://github.com/bigchaindb/bigchaindb/releases)
   and click the "Draft a new release" button
4. Name the tag something like v0.7.0
5. The target should be a specific commit: the one when the update of `bigchaindb/version.py` got merged into master
6. The release title should be something like v0.7.0
7. The description should be copied from the `CHANGELOG.md` file updated above
8. Generate and send the latest `bigchaindb` package to PyPI. Dimi and Sylvain can do this, maybe others
9. Login to readthedocs.org as a maintainer of the BigchainDB Server docs.
   Go to Admin --> Versions and under **Choose Active Versions**, make sure that the new version's tag is
   "Active" and "Public"

After the release:

1. Update `bigchaindb/version.py` again, to be something like 0.8.0.dev (with a dev on the end).
This is so people reading the latest docs will know that they're for the latest (master branch)
version of BigchainDB Server, not the docs at the time of the most recent release (which are also
available).
