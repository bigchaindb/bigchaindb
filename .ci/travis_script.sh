#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
else
  docker-compose -f docker-compose.travis.yml run --rm --no-deps bdb pytest -v --cov=bigchaindb
fi
