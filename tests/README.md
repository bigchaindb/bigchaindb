# BigchainDB Server Tests

## The bigchaindb/tests/ Folder

The `bigchaindb/tests/` folder is where all the tests for BigchainDB Server live. Most of them are unit tests. Integration tests are in the [`bigchaindb/tests/integration/` folder](./integration/).

A few notes:

- [`bigchaindb/tests/common/`](./common/) contains self-contained tests only testing
  [`bigchaindb/common/`](../bigchaindb/common/)
- [`bigchaindb/tests/db/`](./db/) contains tests requiring the database backend (e.g. RethinkDB)

## Pytest Customizations

Customizations we've added to `pytest`:

- `--database-backend`: Defines the backend to use for the tests. Must be one of the backends
  available in the [server configuration](https://docs.bigchaindb.com/projects/server/en/latest/server-reference/configuration.html)
