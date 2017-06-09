#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == mongodb && \
    "${BIGCHAINDB_DATABASE_SSL}" == false ]]; then
  pytest -sv --database-backend=mongodb --cov=bigchaindb
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == mongodb && \
    "${BIGCHAINDB_DATABASE_SSL}" == true ]]; then
  pytest -sv --database-backend=mongodb-ssl --cov=bigchaindb -m bdb_ssl
else
  pytest -sv -n auto --cov=bigchaindb
fi
