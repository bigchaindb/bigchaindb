# BigchainDB Server Tests

## The bigchaindb/tests/ Folder

The `bigchaindb/tests/` folder is where all the tests for BigchainDB Server live. Most of them are unit tests. Integration tests are in the [`bigchaindb/tests/integration/` folder](./integration/).

A few notes:

- [`bigchaindb/tests/common/`](./common/) contains self-contained tests only testing
  [`bigchaindb/common/`](../bigchaindb/common/)
- [`bigchaindb/tests/db/`](./db/) contains tests requiring the database backend (e.g. RethinkDB)


## Writing Tests

We write unit and integration tests for our Python code using the [pytest](http://pytest.org/latest/) framework. You can use the tests in the `bigchaindb/tests/` folder as templates or examples.


## Running Tests

### Running Tests Directly

If you installed BigchainDB Server using `pip install bigchaindb`, then you didn't install the tests. Before you can run all the tests, you must install BigchainDB from source. The [`bigchaindb/CONTRIBUTING.md` file](../CONTRIBUTING.md) has instructions for how to do that.

Next, make sure you have RethinkDB running in the background (e.g. using `rethinkdb --daemon`).

Now you can run all tests using:
```text
py.test -v
```

or, if that doesn't work, try:
```text
python -m pytest -v
```

or:
```text
python setup.py test
```

How does `python setup.py test` work? The documentation for [pytest-runner](https://pypi.python.org/pypi/pytest-runner) explains.

The `pytest` command has many options. If you want to learn about all the things you can do with pytest, see [the pytest documentation](http://pytest.org/latest/). We've also added a customization to pytest:

`--database-backend`: Defines the backend to use for the tests.
It must be one of the backends available in the [server configuration](https://docs.bigchaindb.com/projects/server/en/latest/server-reference/configuration.html).


### Running Tests with Docker Compose

You can also use [Docker Compose](https://docs.docker.com/compose/) to run all the tests.

First, start `RethinkDB` in the background:

```text
$ docker-compose up -d rdb
```

then run the tests using:

```text
$ docker-compose run --rm bdb py.test -v
```


## Automated Testing of All Pull Requests

We use [Travis CI](https://travis-ci.com/), so that whenever someone creates a new BigchainDB pull request on GitHub, Travis CI gets the new code and does _a bunch of stuff_. You can find out what we tell Travis CI to do in [the `.travis.yml` file](.travis.yml): it tells Travis CI how to install BigchainDB, how to run all the tests, and what to do "after success" (e.g. run `codecov`). (We use [Codecov](https://codecov.io/) to get a rough estimate of our test coverage.)


### Tox

We use [tox](https://tox.readthedocs.io/en/latest/) to run multiple suites of tests against multiple environments during automated testing. Generally you don't need to run this yourself, but it might be useful when troubleshooting a failing Travis CI build.

To run all the tox tests, use:
```text
tox
```

or:
```text
python -m tox
```

To run only a few environments, use the `-e` flag:
```text
tox -e {ENVLIST}
```

where `{ENVLIST}` is one or more of the environments specified in the [tox.ini file](../tox.ini).
