<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Backend Interfaces

## Structure

- [`connection.py`](./connection.py): Database connection-related interfaces
- [`query.py`](./query.py): Database query-related interfaces, dispatched through single-dispatch
- [`schema.py`](./schema.py): Database setup and schema-related interfaces, dispatched through
  single-dispatch

Built-in implementations (e.g. [MongoDB's](./localmongodb)) are provided in sub-directories and
have their connection type's location exposed as `BACKENDS` in [`connection.py`](./connection.py).

## Single-Dispatched Interfaces

The architecture of this module is based heavily upon Python's newly-introduced [single-dispatch
generic functions](https://www.python.org/dev/peps/pep-0443/). Single-dispatch is convenient,
because it allows Python, rather than something we design ourselves, to manage the dispatching of
generic functions based on certain conditions being met (e.g. the database backend to use).

To see what this looks like in BigchainDB, first note that our backend interfaces have been
configured to dispatch based on a backend's **connection type**.

Call `bigchaindb.backend.connect()` to create an instance of a `Connection`:

```python
from bigchaindb.backend import connect
connection = connect()  # By default, uses the current configuration for backend, host, port, etc.
```

Then, we can call a backend function by directly calling its interface:

```python
from bigchaindb.backend import query
query.write_transaction(connection, ...)
```

Notice that we don't need to care about which backend implementation to use or how to access it.
Code can simply call the base interface function with a `Connection` instance, and single-dispatch
will handle routing the call to the actual implementation.

BigchainDB will load and register the configured backend's implementation automatically (see
`bigchaindb.backend.connect()`), so you should always just be able to call an interface function if
you have a `Connection` instance. A few helper utilities (see [`backend/utils.py`](./utils.py)) are
also provided to make registering new backend implementations easier.
