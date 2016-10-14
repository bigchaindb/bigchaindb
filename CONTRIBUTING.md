# How to Contribute to the BigchainDB Project

There are many ways you can contribute to the BigchainDB project, some very easy and others more involved. We want to be friendly and welcoming to all potential contributors, so we ask that everyone involved abide by some simple guidelines outlined in our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Easy Ways to Contribute

The BigchainDB community has a Google Group and a Gitter chatroom. Our [Community page](https://www.bigchaindb.com/community) has more information about those.

You can also follow us on Twitter [@BigchainDB](https://twitter.com/BigchainDB) or read [our blog on Medium](https://medium.com/the-bigchaindb-blog).

If you want to file a bug report, suggest a feature, or ask a code-related question, please go to the `bigchaindb/bigchaindb` repository on GitHub and [create a new Issue](https://github.com/bigchaindb/bigchaindb/issues/new). (You will need a [GitHub account](https://github.com/signup/free) (free).) Please describe the issue clearly, including steps to reproduce when it is a bug.

## How to Contribute Code or Documentation

### Step 0 - Decide on an Issue to Resolve, or Create One

We want you to feel like your contributions (pull requests) are welcome, but if you contribute something unnecessary, unwanted, or perplexing, then your experience may be unpleasant. Your pull request may sit gathering dust as everyone scratches their heads wondering what to do with it.

To prevent that situation, we ask that all pull requests should resolve, address, or fix an existing issue. If there is no existing issue, then you should create one first. That way there can be commentary and discussion first, and you can have a better idea of what to expect when you create a corresponding pull request.

When you submit a pull request, please mention the issue (or issues) that it resolves, e.g. "Resolves #123".

Exception: hotfixes and minor changes don't require a pre-existing issue, but please write a thorough pull request description.

### Step 1 - Prepare and Familiarize Yourself

To contribute code or documentation, you need a [GitHub account](https://github.com/signup/free).

Familiarize yourself with how we do coding and documentation in the BigchainDB project, including:

* [our Python Style Guide](PYTHON_STYLE_GUIDE.md) (includes how we write tests)
* [our documentation strategy](./docs/README.md) (including in-code documentation)
* the GitHub Flow (workflow)
    * [GitHub Guide: Understanding the GitHub Flow](https://guides.github.com/introduction/flow/)
    * [Scott Chacon's blog post about GitHub Flow](http://scottchacon.com/2011/08/31/github-flow.html)
* [semantic versioning](http://semver.org/)

### Step 2 - Install some Dependencies

* [Install RethinkDB Server](https://rethinkdb.com/docs/install/)
* Make sure you have Python 3.4+ (preferably in a virtualenv)
* [Install BigchaindB Server's OS-level dependencies](https://docs.bigchaindb.com/projects/server/en/latest/appendices/install-os-level-deps.html)
* [Make sure you have the latest Python 3 version of pip and setuptools](https://docs.bigchaindb.com/projects/server/en/latest/appendices/install-latest-pip.html)

### Step 3 - Fork bigchaindb on GitHub

In your web browser, go to [the BigchainDB repository on GitHub](https://github.com/bigchaindb/bigchaindb) and click the `Fork` button in the top right corner. This creates a new Git repository named `bigchaindb` in _your_ GitHub account.

### Step 4 - Clone Your Fork

(This only has to be done once.) In your local terminal, use Git to clone _your_ `bigchaindb` repository to your local computer. Also add the original GitHub bigchaindb/bigchaindb repository as a remote named `upstream` (a convention):
```text
git clone git@github.com:your-github-username/bigchaindb.git
cd bigchaindb
git remote add upstream git@github.com:bigchaindb/bigchaindb.git
```

### Step 5 - Fetch and Merge the Latest from `upstream/master`

Switch to the `master` branch locally, fetch all `upstream` branches, and merge the just-fetched `upstream/master` branch with the local `master` branch:
```text
git checkout master
git fetch upstream
git merge upstream/master
```

### Step 6 - Install the Python module and the CLI

In order to use and run the source you just cloned from your fork, you need to install BigchainDB on your computer.
The core of BigchainDB is a Python module you can install using the standard [Python packaging tools](http://python-packaging-user-guide.readthedocs.org/en/latest/).
We highly suggest you use `pip` and `virtualenv` to manage your local development.
If you need more information on how to do that, refer to the *Python Packaging User Guide* to [install `pip`](http://python-packaging-user-guide.readthedocs.org/en/latest/installing/#requirements-for-installing-packages) and to [create your first `virtualenv`](http://python-packaging-user-guide.readthedocs.org/en/latest/installing/#creating-virtual-environments).

Once you have `pip` installed and (optionally) you are in a virtualenv, go to the root of the repository (i.e. where the `setup.py` file is), and type:
```text
pip install -e .[dev]
```

This will install the BigchainDB Python module, the CLI, and all the dependencies useful for contributing to the development of BigchainDB.
How? Let's split the command down into its components:
 - `pip` is the Python command to install packages
 - `install` tells pip to use the *install* action
 - `-e` installs a project in [editable mode](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs)
 - `.` installs what's in the current directory
 - `[dev]` adds some [extra requirements](https://pythonhosted.org/setuptools/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies) to the installation. (If you are curious, open `setup.py` and look for `dev` in the `extras_require` section.)

Aside: An alternative to `pip install -e .[dev]` is `python setup.py develop`.


### Step 7 - Create a New Branch for Each Bug/Feature

If your new branch is to **fix a bug** identified in a specific GitHub Issue with number `ISSNO`, then name your new branch `bug/ISSNO/short-description-here`. For example, `bug/67/fix-leap-year-crash`.

If your new branch is to **add a feature** requested in a specific GitHub Issue with number `ISSNO`, then name your new branch `feat/ISSNO/short-description-here`. For example, `feat/135/blue-background-on-mondays`.

Otherwise, please give your new branch a short, descriptive, all-lowercase name.
```text
git checkout -b new-branch-name
```

### Step 8 - Make Edits, git add, git commit

With your new branch checked out locally, make changes or additions to the code or documentation. Remember to:

* follow [our Python Style Guide](PYTHON_STYLE_GUIDE.md).
* write and run tests for any new or changed code. There's a section in [our Python Style Guide](PYTHON_STYLE_GUIDE.md) about writing and running tests.
* add or update documentation as necessary. Follow [our documentation strategy](./docs/README.md).

As you go, git add and git commit your changes or additions, e.g.
```text
git add new-or-changed-file-1
git add new-or-changed-file-2
git commit -m "Short description of new or changed things"
```

You will want to merge changes from upstream (i.e. the original repository) into your new branch from time to time, using something like:
```text
git fetch upstream
git merge upstream/master
```

Once you're done commiting a set of new things and you're ready to submit them for inclusion, please be sure to run all the tests (as per the instructions at the end of our [Python Style Guide](PYTHON_STYLE_GUIDE.md)).

If your addition or change is substantial, then please add a line or two to the [CHANGELOG.md file](https://github.com/bigchaindb/bigchaindb/blob/master/CHANGELOG.md), following the guidelines given at the top of that file.

(When you submit your pull request [following the instructions below], we run all the tests automatically, so we will see if some are failing. If you don't know why some tests are failing, you can still submit your pull request, but be sure to note the failing tests and to ask for help with resolving them.)

### Step 9 - Push Your New Branch to origin

Make sure you've commited all the additions or changes you want to include in your pull request. Then push your new branch to origin (i.e. _your_ remote bigchaindb repository).
```text
git push origin new-branch-name
```

### Step 10 - Create a Pull Request 

Go to the GitHub website and to _your_ remote bigchaindb repository (i.e. something like https://github.com/your-user-name/bigchaindb). 

See [GitHub's documentation on how to initiate and send a pull request](https://help.github.com/articles/using-pull-requests/). Note that the destination repository should be `bigchaindb/bigchaindb` and the destination branch will be `master` (usually, and if it's not, then we can change that if necessary).

If this is the first time you've submitted a pull request to BigchainDB, then you must read and accept the Contributor License Agreement (CLA) before we can merge your contributions. That can be found at [https://www.bigchaindb.com/cla](https://www.bigchaindb.com/cla).

Once you accept and submit the CLA, we'll email you with further instructions. (We will send you a long random string to put in the comments section of your pull request, along with the text, "I have read and agree to the terms of the BigchainDB Contributor License Agreement.")

Someone will then merge your branch or suggest changes. If we suggest changes, you won't have to open a new pull request, you can just push new code to the same branch (on `origin`) as you did before creating the pull request.

## Quick Links

* [BigchainDB Community links](https://www.bigchaindb.com/community)
* [General GitHub Documentation](https://help.github.com/)
* [Code of Conduct](./CODE_OF_CONDUCT.md)
* [BigchainDB Licenses](./LICENSES.md)
* [Contributor License Agreement](https://www.bigchaindb.com/cla)

(Note: GitHub automatically links to CONTRIBUTING.md when a contributor creates an Issue or opens a Pull Request.)
