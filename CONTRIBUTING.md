# How to Contribute to the BigchainDB Project

There are many ways you can contribute to the BigchainDB project, some very easy and others more involved. We want to be friendly and welcoming to all potential contributors, so we ask that everyone involved abide by some simple guidelines outlined in our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Easy Ways to Contribute

The BigchainDB community has a Google Group and a Slack chat. Our [Community page](https://www.bigchaindb.com/community) has more information about those.

You can also follow us on Twitter [@BigchainDB](https://twitter.com/BigchainDB).

If you want to file a bug report, suggest a feature, or ask a code-related question, please go to the `BigchainDB/bigchaindb` repository on GitHub and [create a new Issue](https://github.com/bigchaindb/bigchaindb/issues/new). (You will need a [GitHub account](https://github.com/signup/free) (free).) Please describe the issue clearly, including steps to reproduce when it is a bug.

## How to Contribute Code or Documentation

### Step 0 - Prepare and Familiarize Yourself

To contribute code or documentation, you need a [GitHub account](https://github.com/signup/free).

Familiarize yourself with how we do coding and documentation in the BigchainDB project, including:

* our Python Style Guide (coming soon)
* [our documentation strategy](./docs/README.md) (including code documentation)
* the GitHub Flow (workflow)
    * [GitHub Guide: Understanding the GitHub Flow](https://guides.github.com/introduction/flow/)
    * [Scott Chacon's blog post about GitHub Flow](http://scottchacon.com/2011/08/31/github-flow.html)
    * Note that we call the main branch `develop` rather than `master`
* [semantic versioning](http://semver.org/)

### Step 1 - Fork bigchaindb on GitHub

In your web browser, go to [the BigchainDB repository on GitHub](https://github.com/bigchaindb/bigchaindb) and click the `Fork` button in the top right corner. This creates a new Git repository named `bigchaindb` in _your_ GitHub account.

### Step 2 - Clone Your Fork

(This only has to be done once.) In your local terminal, use Git to clone _your_ `bigchaindb` repository to your local computer. Also add the original GitHub bigchaindb/bigchaindb repository as a remote named `upstream` (a convention):
```shell
git clone git@github.com:your-github-username/bigchaindb.git
cd bigchaindb
git add upstream git@github.com:BigchainDB/bigchaindb.git
```

### Step 3 - Fetch and Merge the Latest from `upstream/develop`

Switch to the `develop` branch locally, fetch all `upstream` branches, and merge the just-fetched `upstream/develop` branch with the local `develop` branch:
```shell
git checkout develop
git fetch upstream
git merge upstream/develop
```

### Step 4 - Create a New Branch for Each Bug/Feature

If your new branch is to **fix a bug** identified in a specific GitHub Issue with number `ISSNO`, then name your new branch `bug/ISSNO/short-description-here`. For example, `bug/67/fix-leap-year-crash`.

If your new branch is to **add a feature** requested in a specific GitHub Issue with number `ISSNO`, then name your new branch `feat/ISSNO/short-description-here`. For example, `feat/135/blue-background-on-mondays`.

Otherwise, please give your new branch a short, descriptive, all-lowercase name.
```shell
git checkout -b new-branch-name
```

### Step 5 - Make Edits, git add, git commit

With your new branch checked out locally, make changes or additions to the code or documentation, git add them, and git commit them.
```shell
git add new-or-changed-file
git commit -m "Short description of new or changed things"
```

Remember to write tests for new code. If you don't, our code (test) coverage will go down, and we won't be able to accept your code. (We have some hard checks that run on all new pull requests and code coverage is one of them.)

Please run all existing tests to make sure you didn't break something. Do:
```shell
py.test -v
```

Remember to write or modify documentation to reflect your additions or changes.

You will want to merge changes from upstream (i.e. the original repository) into your new branch from time to time, using something like:
```shell
git fetch upstream
git merge upstream/develop
```

### Step 6 - Push Your New Branch to origin

Make sure you've commited all the additions or changes you want to include in your pull request. Then push your new branch to origin (i.e. _your_ remote bigchaindb repository).
```shell
git push origin new-branch-name
```

### Step 7 - Create a Pull Request 

Go to the GitHub website and to _your_ remote bigchaindb repository (i.e. something like https://github.com/your-user-name/bigchaindb). 

See [GitHub's documentation on how to initiate and send a pull request](https://help.github.com/articles/using-pull-requests/). Note that the destination repository should be `BigchainDB/bigchaindb` and the destination branch will be `develop` (usually, and if it's not, then we can change that if necessary).

If this is the first time you've submitted a pull request to BigchainDB, then you must read and accept the Contributor License Agreement (CLA) before we can merge your contributions. That can be found at [https://www.bigchaindb.com/cla](https://www.bigchaindb.com/cla).

Once you accept and submit the CLA, we'll email you with further instructions. (We will send you a long random string to put in the comments section of your pull request, along with the text, "I have read and agree to the terms of the BigchainDB Contributor License Agreement.")

Someone will then merge your branch or suggest changes. If we suggsest changes, you won't have to open a new pull request, you can just push new code to the same branch (on `origin`) as you did before creating the pull request.

## Quick Links

* [BigchainDB Community links](https://www.bigchaindb.com/community) (e.g. mailing list, Slack)
* [General GitHub Documentation](https://help.github.com/)
* [Code of Conduct](./CODE_OF_CONDUCT.md)
* [BigchainDB Licenses](./LICENSES.md)
* [Contributor License Agreement](https://www.bigchaindb.com/cla)

(Note: GitHub automatically links to CONTRIBUTING.md when a contributor creates an Issue or opens a Pull Request.)