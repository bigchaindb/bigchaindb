# Backend Interfaces

## Structure

- [`changefeed.py`](./changefeed.py): Changefeed-related interfaces
- [`connection.py`](./connection.py): Database connection-related interfaces
- [`query.py`](./query.py): Database query-related interfaces, dispatched through single-dispatch
- [`schema.py`](./schema.py): Database setup and schema-related interfaces, dispatched through
  single-dispatch

Built-in implementations (e.g. [RethinkDB's](./rethinkdb)) are provided in sub-directories and
have their connection type's location exposed as `BACKENDS` in [`connection.py`](./connection.py).

## Single-Dispatch

The architecture of this module is based heavily upon Python's newly-introduced [single-dispatch
generic functions](https://www.python.org/dev/peps/pep-0443/). Single-dispatch is convenient,
because it allows Python, rather than something we design ourselves, to manage the dispatching of
generic functions based on certain conditions being met (e.g. the database backend to use).

BigchainDB has been set up to make the registration of backend implementation automatic, so that
you don't have to worry about loading the correct implementation. Backend functions can be called
directly through their interfaces; single-dispatch will handle the routing to the actual
implementation.

To see how this might work, we first note we've set up dispatching based on a backend's **connection
type**. To grab one, call `bigchaindb.backend.connect()`:

```python
from bigchaindb.backend import connect
connection = connect()  # By default, uses the current configuration for backend, host, port, etc.
```

Then, we can call a backend function by directly calling its interface:

```python
from bigchaindb.backend import query
query.write_transaction(connection, ...)
```

Notice that we don't need to care about which implementation we're using, or how to access it.
Simply call the base interface function with the connection class, and single-dispatch will handle
the call to the implementation.
