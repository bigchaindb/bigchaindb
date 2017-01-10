#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == mongodb ]]; then
  pytest -v --database-backend=mongodb --cov=bigchaindb
else
  pytest -v -n auto --cov=bigchaindb
fi
