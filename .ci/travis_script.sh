#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == localmongodb && \
    -z "${BIGCHAINDB_DATABASE_SSL}" ]]; then
    # Run the full suite of tests for MongoDB over an unsecure connection
  pytest -sv --database-backend=localmongodb --cov=bigchaindb -m tendermint
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == localmongodb && \
    "${BIGCHAINDB_DATABASE_SSL}" == true ]]; then
    # Run a sub-set of tests over SSL; those marked as 'pytest.mark.bdb_ssl'.
  pytest -sv --database-backend=localmongodb-ssl --cov=bigchaindb -m bdb_ssl
else
  # Run the full suite of tests for RethinkDB (the default backend when testing)
  pytest -sv -m "serial"
  pytest -sv --cov=bigchaindb -m "not serial"
fi
