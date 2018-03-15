#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
else
  docker-compose run --rm --no-deps bigchaindb pytest -v --cov=bigchaindb
fi
