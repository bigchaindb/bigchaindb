#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == mongodb ]]; then
  pytest -v --database-backend=mongodb --cov=bigchaindb
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == mongodb-ssl ]]; then
  pytest -v --database-backend=mongodb-ssl --cov=bigchaindb -m bdb_ssl
else
  pytest -v -n auto --cov=bigchaindb
fi
