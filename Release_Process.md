# Our Release Process

The release process for BigchainDB server differs slightly depending on whether it's a minor or a patch release.

BigchainDB follows [semantic versioning](http://semver.org/) (i.e. MAJOR.MINOR.PATCH), taking into account
that [major version 0.x does not export a stable API](http://semver.org/#spec-item-4).

## Minor release

A minor release is preceeded by a feature freeze and created from the 'master' branch. This is a summary of the steps we go through to release a new minor version of BigchainDB Server.

1. Update the `CHANGELOG.md` file in master
1. In `k8s/bigchaindb/bigchaindb-dep.yaml`, find the line of the form `image: bigchaindb/bigchaindb:0.8.1` and change the version number to the new version number, e.g. `0.9.0`. (This is the Docker image that Kubernetes should pull from Docker Hub.) Commit that change to master
1. Create and checkout a new branch for the minor release, named after the minor version, without a preceeding 'v', e.g. `git checkout -b 0.9` (*not* 0.9.0, this new branch will be for e.g. 0.9.0, 0.9.1, 0.9.2, etc. each of which will be identified by a tagged commit)
1. In `bigchaindb/version.py`, update `__version__` and `__short_version__`, e.g. to `0.9` and `0.9.0` (with no `.dev` on the end)
1. Commit that change, and push the new branch to GitHub
1. Follow steps outlined in [Common Steps](#common-steps)
1. In 'master' branch, Edit `bigchaindb/version.py`, increment the minor version to the next planned release, e.g. `0.10.0.dev`. This is so people reading the latest docs will know that they're for the latest (master branch) version of BigchainDB Server, not the docs at the time of the most recent release (which are also available).
1. Go to [Docker Hub](https://hub.docker.com/), sign in, go to Settings - Build Settings, and under the build with Docker Tag Name equal to `latest`, change the Name to the number of the new release, e.g. `0.9`

Congratulations, you have released BigchainDB!

## Patch release

A patch release is similar to a minor release, but piggybacks on an existing minor release branch:

1. Check out the minor release branch, e.g. `0.9`
1. Apply the changes you want, e.g. using `git cherry-pick`.
1. Update the `CHANGELOG.md` file
1. Increment the patch version in `bigchaindb/version.py`, e.g. `0.9.1`
1. Commit that change
1. In `k8s/bigchaindb/bigchaindb-dep.yaml`, find the line of the form `image: bigchaindb/bigchaindb:0.9.0` and change the version number to the new version number, e.g. `0.9.1`. (This is the Docker image that Kubernetes should pull from Docker Hub.)
1. Commit that change
1. Push the updated minor release branch to GitHub
1. Follow steps outlined in [Common Steps](#common-steps)
1. Cherry-pick the `CHANGELOG.md` update commit (made above) to the `master` branch

## Common steps

These steps are common between minor and patch releases:

1. Go to the [bigchaindb/bigchaindb Releases page on GitHub](https://github.com/bigchaindb/bigchaindb/releases)
   and click the "Draft a new release" button
1. Fill in the details:
   - Tag version: version number preceeded by 'v', e.g. "v0.9.1"
   - Target: the release branch that was just pushed
   - Title: Same as tag name above, e.g "v0.9.1"
   - Description: The body of the changelog entry (Added, Changed, etc.)
1. Click "Publish release" to publish the release on GitHub
1. Make sure your local Git is in the same state as the release: e.g. `git fetch <remote-name>` and `git checkout v0.9.1`
1. Make sure you have a `~/.pypirc` file containing credentials for PyPI
1. Do a `make release` to build and publish the new `bigchaindb` package on PyPI
1. [Login to readthedocs.org](https://readthedocs.org/accounts/login/)
   as a maintainer of the BigchainDB Server docs, and:
   - Go to Admin --> Advanced Settings
     and make sure that "Default branch:" (i.e. what "latest" points to)
     is set to the new release's tag, e.g. `v0.9.1`.
     (Don't miss the 'v' in front.)
   - Go to Admin --> Versions
     and under **Choose Active Versions**, do these things:
     1. Make sure that the new version's tag is "Active" and "Public"
     2. Make sure the new version's branch
        (without the 'v' in front) is _not_ active.
     3. Make sure the **stable** branch is _not_ active.
     4. Scroll to the bottom of the page and click the Submit button.
