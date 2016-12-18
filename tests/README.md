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

You can run all tests using:
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

If you want to learn about all the things you can do with pytest, see [the pytest documentation](http://pytest.org/latest/).


### Our pytest Customizations

Customizations we've added to pytest:

- `--database-backend`: Defines the backend to use for the tests. Must be one of the backends
  available in the [server configuration](https://docs.bigchaindb.com/projects/server/en/latest/server-reference/configuration.html)




## Automated testing of pull requests

We use [Travis CI](https://travis-ci.com/), so that whenever someone creates a new BigchainDB pull request on GitHub, Travis CI gets the new code and does _a bunch of stuff_. You can find out what we tell Travis CI to do in [the `.travis.yml` file](.travis.yml): it tells Travis CI how to install BigchainDB, how to run all the tests, and what to do "after success" (e.g. run `codecov`). (We use [Codecov](https://codecov.io/) to get a rough estimate of our test coverage.)


### Tox

We use [tox](https://tox.readthedocs.io/en/latest/) to run multiple suites of tests against multiple environments during automated testing. Generally you don't need to run this yourself, but it might be useful when troubleshooting a failing CI build.

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

where `{ENVLIST}` is one or more of the environments specified in the [tox.ini file](tox.ini).