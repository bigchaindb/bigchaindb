#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
elif [[ ${BIGCHAINDB_CI_ABCI} == 'enable' ]]; then
  docker-compose exec bigchaindb pytest -v -m abci
elif [[ ${BIGCHAINDB_ACCEPTANCE_TEST} == 'enable' ]]; then
    ./run-acceptance-test.sh
else
  docker-compose exec bigchaindb pytest -v --cov=bigchaindb
fi
