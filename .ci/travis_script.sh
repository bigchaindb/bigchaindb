#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
elif [[ ${BIGCHAINDB_CI_ABCI} == 'enable' ]]; then
  docker-compose exec bigchaindb pytest -v -m abci
else
  docker-compose exec bigchaindb pytest -v --cov=bigchaindb
fi
