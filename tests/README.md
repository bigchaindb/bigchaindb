# Tests

## Test Structure

Generally all tests are meant to be unit tests, with the exception of those in the [`integration/` folder](./integration/).

A few notes:

- [`common/`](./common/) contains self-contained tests only testing
  [`bigchaindb/common/`](../bigchaindb/common/)
- [`db/`](./db/) contains tests requiring the database backend (e.g. RethinkDB)

## Pytest Customizations

Customizations we've added to `pytest`:

- `--database-backend`: Defines the backend to use for the tests. Must be one of the backends
  available in the [server configuration](https://docs.bigchaindb.com/projects/server/en/latest/server-reference/configuration.html)
