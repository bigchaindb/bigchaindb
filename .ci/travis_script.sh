#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
elif [[ ${BIGCHAINDB_CI_ABCI} == 'enable' ]]; then
  docker-compose -f docker-compose.travis.yml exec bdb pytest -v -m abci
else
  docker-compose run --rm --no-deps bigchaindb pytest -v --cov=bigchaindb
fi
