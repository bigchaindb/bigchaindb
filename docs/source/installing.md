# Installing BigchainDB

We're developing BigchainDB on Ubuntu 14.04, but it should work on any OS that runs RethinkDB Server and Python 3.4+. (BigchainDB is built on top of RethinkDB Server.)

## Install and Run RethinkDB Server

The RethinkDB documentation has instructions for how to install RethinkDB Server on a variety of operating systems. Do that (using their instructions for your OS): [Install RethinkDB Server](http://rethinkdb.com/docs/install/).

RethinkDB Server doesn't require any special configuration. You can run it by opening a Terminal and entering:
```shell
$ rethinkdb
```

## Install Python 3.4+

If you don't already have it, then you should [install Python 3.4+](https://www.python.org/downloads/) (maybe in a virtual environment, so it doesn't conflict with other Python projects you're working on).

## Install BigchainDB

BigchainDB has some OS-level dependencies. In particular, you need to install the OS-level dependencies for the Python **cryptography** package. Instructions for installing those dependencies on your OS can be found in the [cryptography package documentation](https://cryptography.io/en/latest/installation/).

On Ubuntu 14.04, we found that the following was enough (YMMV):
```shell
$ sudo apt-get update
$ sudo apt-get install libffi-dev g++ libssl-dev python3-dev
```

With OS-level dependencies installed, you can install BigchainDB with `pip` or from source.

### How to Install BigchainDB with `pip`

BigchainDB is distributed as a Python package on PyPI so you can install it using `pip`. First, make sure you have a version of `pip` installed for Python 3.4+:
```shell
$ pip -V
```

If it says the associated Python version is Python 3.4+, then you can do:
```shell
$ pip install bigchaindb
```

If it says that `pip` isn't installed, or it says `pip` is associated with a Python version less then 3.4, then you must install a `pip` version associated with Python 3.4+. See [the `pip` installation instructions](https://pip.pypa.io/en/stable/installing/).

On Ubuntu 14.04, we found that this works:
```shell
$ sudo apt-get python3-pip
$ sudo pip3 install bigchaindb
```

(It might not be necessary to use `sudo` in the last command above, but we found that it _was_ necessary for Ubuntu 14.04 on an Amazon Web Services (AWS) instance.)

In general, once you have a version of `pip` associated with Python 3.4+, then you can install BigchainDB using `pip install bigchaindb` or `pipVER install bigchaindb` where `pipVER` is replaced by whatever you must use to call a version of `pip` associated with Python 3.4+ (e.g. `pip3`).

### How to Install BigchainDB from Source

BigchainDB is in its early stages and being actively developed on its [GitHub repository](https://github.com/bigchaindb/bigchaindb). Contributions are highly appreciated.

Clone the public repository:
```shell
$ git clone git@github.com:bigchaindb/bigchaindb.git
```

Install from the source:
```shell
$ python setup.py install
```

### How to Install BigchainDB Using Docker

Coming soon...

## Run BigchainDB

After installing BigchainDB, run it with:
```shell
$ bigchaindb start
```

During its first run, BigchainDB takes care of configuring a single node environment.
