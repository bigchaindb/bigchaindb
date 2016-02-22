# BigchainDB

[![Join the chat at https://gitter.im/bigchaindb/bigchaindb](https://badges.gitter.im/bigchaindb/bigchaindb.svg)](https://gitter.im/bigchaindb/bigchaindb?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![PyPI](https://img.shields.io/pypi/v/bigchaindb.svg)](https://pypi.python.org/pypi/BigchainDB)
[![Travis branch](https://img.shields.io/travis/bigchaindb/bigchaindb/develop.svg)](https://travis-ci.org/bigchaindb/bigchaindb)
[![Codecov branch](https://img.shields.io/codecov/c/github/bigchaindb/bigchaindb/develop.svg)](https://codecov.io/github/bigchaindb/bigchaindb?branch=develop)
[![Documentation Status](https://readthedocs.org/projects/bigchaindb/badge/?version=develop)](http://bigchaindb.readthedocs.org/en/develop/?badge=develop)

## Documentation

Documentation is available at https://bigchaindb.readthedocs.org/

## Getting started

### Install RethinkDB

#### On Ubuntu
```sh
# install rethinkdb https://rethinkdb.com/docs/install/ubuntu/
$ source /etc/lsb-release && echo "deb http://download.rethinkdb.com/apt $DISTRIB_CODENAME main" | sudo tee /etc/apt/sources.list.d/rethinkdb.list
$ wget -qO- http://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -
$ sudo apt-get update
$ sudo apt-get install rethinkdb

# start rethinkdb
$ rethinkdb
```

#### On other platforms
To install RethinkDB on other platform, please refer to [the official documentation](https://rethinkdb.com/docs/install/).

### Install BigchainDB
```sh
$ pip install bigchaindb
```

### Running BigchainDB
Currently BigchainDB only supports Python 3.4+


Start the main process. If it's the first time `bigchaindb` will generate a default
configuration file for you.
```sh
$ bigchaindb start
```

Generate some tests transactions:

```sh
$ bigchaindb-benchmark load # add '-m' if you want to use all your cores
```

To know more about the bigchain command run
```sh
$ bigchaindb -h
```

#### Importing `BigchainDB` from the interpreter (python/ipython)
Make sure your `rethinkdb` process is running.

```python
>>> from bigchaindb import Bigchain
>>> b = Bigchain()
>>> b.me
'2B8C8PJxhycFzn4wncRhBNmMWwE5Frr9nLBUa1dGGxj5W'
```

#### Configuration

BigchainDB creates a default configuration file on `$HOME/.bigchaindb` on the
first run.

```sh
$ bigchaindb show-config
```

#### Testing

```
$ py.test -v
```

#### Monitoring

BigchainDB uses [statsd](https://github.com/etsy/statsd) for monitoring.  To fully take advantage of this functionality requires some additional infrastructure: an agent to listen for metrics (e.g. [telegraf](https://github.com/influxdata/telegraf)), a time-series database (e.g. [influxdb](https://influxdata.com/time-series-platform/influxdb/), and a frontend to display analytics (e.g. [Grafana](http://grafana.org/)).

For ease of use, we've provided a docker compose file that sets up all these services for testing. Simply run in the BigchainDB directory:

```sh
$ docker-compose -f docker-compose-monitor.yml build
$ docker-compose -f docker-compose-monitor.yml up
```

and point a browser tab to `http://localhost:3000/dashboard/script/bigchaindb_dashboard.js`.  Login and password are `admin` by default.  If BigchainDB is running and processing transactions, you should see analytics—if not, start BigchainDB as above, and refresh the page after a few seconds.

If you're not interested in monitoring, don't worry: BigchainDB will function just fine without any monitoring setup.

Feel free to modify the [custom Grafana dashboard](https://github.com/rhsimplex/grafana-bigchaindb-docker/blob/master/bigchaindb_dashboard.js) to your liking!