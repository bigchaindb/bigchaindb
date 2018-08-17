#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
elif [[ ${BIGCHAINDB_CI_ABCI} == 'enable' ]]; then
  docker-compose exec bigchaindb pytest -v -m abci
elif [[ ${BIGCHAINDB_ACCEPTANCE_TEST} == 'enable' ]]; then
    ./run-acceptance-test.sh
else
  docker-compose exec bigchaindb pytest -v --cov=bigchaindb --cov-report xml:htmlcov/coverage.xml
fi
