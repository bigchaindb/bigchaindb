<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Our Release Process

## Notes

BigchainDB follows
[the Python form of Semantic Versioning](https://packaging.python.org/tutorials/distributing-packages/#choosing-a-versioning-scheme)
(i.e. MAJOR.MINOR.PATCH),
which is almost identical
to [regular semantic versioning](http://semver.org/), but there's no hyphen, e.g.

- `0.9.0` for a typical final release
- `4.5.2a1` not `4.5.2-a1` for the first Alpha release
- `3.4.5rc2` not `3.4.5-rc2` for Release Candidate 2

**Note 1:** For Git tags (which are used to identify releases on GitHub), we append a `v` in front. For example, the Git tag for version `2.0.0a1` was `v2.0.0a1`.

**Note 2:** For Docker image tags (e.g. on Docker Hub), we use longer version names for Alpha, Beta and Release Candidate releases. For example, the Docker image tag for version `2.0.0a2` was `2.0.0-alpha2`.

We use `0.9` and `0.9.0` as example version and short-version values below. You should replace those with the correct values for your new version.

We follow [BEP-1](https://github.com/bigchaindb/BEPs/tree/master/1), which is our variant of C4, the Collective Code Construction Contract, so a release is just a [tagged commit](https://git-scm.com/book/en/v2/Git-Basics-Tagging) on the `master` branch, i.e. a label for a particular Git commit.

The following steps are what we do to release a new version of _BigchainDB Server_. The steps to release the Python Driver are similar but not the same.

## Steps

1. Create a pull request where you make the following changes:

   - Update `CHANGELOG.md`
   - Update all Docker image tags in all Kubernetes YAML files (in the `k8s/` directory).
     For example, in the files:

     - `k8s/bigchaindb/bigchaindb-ss.yaml` and
     - `k8s/dev-setup/bigchaindb.yaml`

     find the line of the form `image: bigchaindb/bigchaindb:0.8.1` and change the version number to the new version number, e.g. `0.9.0`. (This is the Docker image that Kubernetes should pull from Docker Hub.)
     Keep in mind that this is a _Docker image tag_ so our naming convention is
     a bit different; see Note 2 in the **Notes** section above.
   - In `bigchaindb/version.py`:
     - update `__version__` to e.g. `0.9.0` (with no `.dev` on the end)
     - update `__short_version__` to e.g. `0.9` (with no `.dev` on the end)
   - In the docs about installing BigchainDB (and Tendermint), and in the associated scripts, recommend/install a version of Tendermint that _actually works_ with the soon-to-be-released version of BigchainDB. You can find all such references by doing a search for the previously-recommended version number, such as `0.31.5`.
   - In `setup.py`, _maybe_ update the development status item in the `classifiers` list. For example, one allowed value is `"Development Status :: 5 - Production/Stable"`. The [allowed values are listed at pypi.python.org](https://pypi.python.org/pypi?%3Aaction=list_classifiers).

2. **Wait for all the tests to pass!**
3. Merge the pull request into the `master` branch.
4. Go to the [bigchaindb/bigchaindb Releases page on GitHub](https://github.com/bigchaindb/bigchaindb/releases)
   and click the "Draft a new release" button.
5. Fill in the details:
   - **Tag version:** version number preceded by `v`, e.g. `v0.9.1`
   - **Target:** the last commit that was just merged. In other words, that commit will get a Git tag with the value given for tag version above.
   - **Title:** Same as tag version above, e.g `v0.9.1`
   - **Description:** The body of the changelog entry (Added, Changed, etc.)
6. Click "Publish release" to publish the release on GitHub.
7. On your local computer, make sure you're on the `master` branch and that it's up-to-date with the `master` branch in the bigchaindb/bigchaindb repository (e.g. `git pull upstream master`). We're going to use that to push a new `bigchaindb` package to PyPI.
8. Make sure you have a `~/.pypirc` file containing credentials for PyPI.
9. Do `make release` to build and publish the new `bigchaindb` package on PyPI. For this step you need to have `twine` installed. If you get an error like `Makefile:135: recipe for target 'clean-pyc' failed` then try doing
   ```text
   sudo chown -R $(whoami):$(whoami) .
   ```
10. [Log in to readthedocs.org](https://readthedocs.org/accounts/login/) and go to the **BigchainDB Server** project, then:
   - Click on "Builds", select "latest" from the drop-down menu, then click the "Build Version:" button.
   - Wait for the build of "latest" to finish. This can take a few minutes.
   - Go to Admin --> Advanced Settings
     and make sure that "Default branch:" (i.e. what "latest" points to)
     is set to the new release's tag, e.g. `v0.9.1`.
     (It won't be an option if you didn't wait for the build of "latest" to finish.)
     Then scroll to the bottom and click "Save".
   - Go to Admin --> Versions
     and under **Choose Active Versions**, do these things:
     1. Make sure that the new version's tag is "Active" and "Public"
     2. Make sure the **stable** branch is _not_ active.
     3. Scroll to the bottom of the page and click "Save".
11. Go to [Docker Hub](https://hub.docker.com/) and sign in, then:
   - Click on "Organizations"
   - Click on "bigchaindb"
   - Click on "bigchaindb/bigchaindb"
   - Click on "Build Settings"
   - Find the row where "Docker Tag Name" equals `latest`
     and change the value of "Name" to the name (Git tag)
     of the new release, e.g. `v0.9.0`.
   - If the release is an Alpha, Beta or Release Candidate release,
     then a new row must be added.
     You can do that by clicking the green "+" (plus) icon.
     The contents of the new row should be similar to the existing rows
     of previous releases like that.
   - Click on "Tags"
   - Delete the "latest" tag (so we can rebuild it)
   - Click on "Build Settings" again
   - Click on the "Trigger" button for the "latest" tag and make sure it worked by clicking on "Tags" again
   - If the release is an Alpha, Beta or Release Candidate release,
     then click on the "Trigger" button for that tag as well.

Congratulations, you have released a new version of BigchainDB Server!
