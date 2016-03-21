# Running Unit Tests

Once you've installed BigchainDB Server, you may want to run all the unit tests. This section explains how.

First of all, if you installed BigchainDB Server using `pip` (i.e. by getting the package from PyPI), then you didn't install the tests. Before you can run all the unit tests, you must [install BigchainDB from source](installing-server.html#how-to-install-bigchaindb-from-source).

To run all the unit tests, first make sure you have RethinkDB running:
```text
$ rethinkdb
```

then in another terminal, do:
```text
$ py.test -v
```

If the above command doesn't work (e.g. maybe you are running in a conda virtual environment), try:
```text
$ python -m pytest -v
```

(We write our unit tests using the [pytest](http://pytest.org/latest/) framework.)

You can also run all unit tests via `setup.py`, using:
```text
$  python setup.py test
```

### Using `docker-compose` to Run the Tests

You can also use `docker-compose` to run the unit tests. (You don't have to start RethinkDB first: `docker-compose` does that on its own, when it reads the `docker-compose.yml` file.)

First, build the images (~once), using:
```text
$ docker-compose build
```

then run the unit tests using:
```text
$ docker-compose run --rm bigchaindb py.test -v
```
