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

**Note 2:** For Docker image tags (e.g. on Docker Hub), we use longer version names for Alpha, Beta and Release Candidate releases. For example, the Docker image tag for version `2.0.0a1` was `2.0.0-alpha`.

We use `0.9` and `0.9.0` as example version and short-version values below. You should replace those with the correct values for your new version.

We follow [BEP-1](https://github.com/bigchaindb/BEPs/tree/master/1), which is our variant of C4, the Collective Code Construction Contract, so a release is just a [tagged commit](https://git-scm.com/book/en/v2/Git-Basics-Tagging) on the `master` branch, i.e. a label for a particular Git commit.

The following steps are what we do to release a new version of _BigchainDB Server_. The steps to release the Python Driver are similar but not the same.

## Steps

1. Create a pull request where you make the following changes:

   - Update `CHANGELOG.md`
   - Update all Docker image tags in all Kubernetes YAML files (in the `k8s/` directory).
     For example, in the files:

     - `k8s/bigchaindb/bigchaindb-dep.yaml` and
     - `k8s/dev-setup/bigchaindb.yaml`

     find the line of the form `image: bigchaindb/bigchaindb:0.8.1` and change the version number to the new version number, e.g. `0.9.0`. (This is the Docker image that Kubernetes should pull from Docker Hub.)
     Keep in mind that this is a _Docker image tag_ so our naming convention is
     a bit different; see Note 2 in the **Notes** section above.
   - In `bigchaindb/version.py`:
     - update `__version__` to e.g. `0.9.0` (with no `.dev` on the end)
     - update `__short_version__` to e.g. `0.9` (with no `.dev` on the end)
   - In `setup.py`, _maybe_ update the development status item in the `classifiers` list. For example, one allowed value is `"Development Status :: 5 - Production/Stable"`. The [allowed values are listed at pypi.python.org](https://pypi.python.org/pypi?%3Aaction=list_classifiers).

1. **Wait for all the tests to pass!**
1. Merge the pull request into the `master` branch.
1. Go to the [bigchaindb/bigchaindb Releases page on GitHub](https://github.com/bigchaindb/bigchaindb/releases)
   and click the "Draft a new release" button.
1. Fill in the details:
   - **Tag version:** version number preceded by `v`, e.g. `v0.9.1`
   - **Target:** the last commit that was just merged. In other words, that commit will get a Git tag with the value given for tag version above.
   - **Title:** Same as tag version above, e.g `v0.9.1`
   - **Description:** The body of the changelog entry (Added, Changed, etc.)
1. Click "Publish release" to publish the release on GitHub.
1. On your local computer, make sure you're on the `master` branch and that it's up-to-date with the `master` branch in the bigchaindb/bigchaindb repository (e.g. `git fetch upstream` and `git merge upstream/master`). We're going to use that to push a new `bigchaindb` package to PyPI.
1. Make sure you have a `~/.pypirc` file containing credentials for PyPI.
1. Do `make release` to build and publish the new `bigchaindb` package on PyPI.
1. [Log in to readthedocs.org](https://readthedocs.org/accounts/login/) and go to the **BigchainDB Server** project, then:
   - Go to Admin --> Advanced Settings
     and make sure that "Default branch:" (i.e. what "latest" points to)
     is set to the new release's tag, e.g. `v0.9.1`.
     (Don't miss the `v` in front.)
   - Go to Admin --> Versions
     and under **Choose Active Versions**, do these things:
     1. Make sure that the new version's tag is "Active" and "Public"
     1. Make sure the **stable** branch is _not_ active.
     1. Scroll to the bottom of the page and click the "Submit" button.
1. Go to [Docker Hub](https://hub.docker.com/), sign in, go to bigchaindb/bigchaindb, and go to Settings --> Build Settings. Find the row where "Docker Tag Name" equals `latest` and change the value of "Name" to the name (Git tag) of the new release, e.g. `v0.9.0`.

Congratulations, you have released a new version of BigchainDB Server!

## Post-Release Steps

In the `master` branch, open `bigchaindb/version.py` and increment the minor version to the next planned release, e.g. `0.10.0.dev`. Note: If you just released `X.Y.Zrc1` then increment the minor version to `X.Y.Zrc2`. This step is so people reading the latest docs will know that they're for the latest (`master` branch) version of BigchainDB Server, not the docs at the time of the most recent release (which are also available).
