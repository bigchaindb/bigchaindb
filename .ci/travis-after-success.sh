#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]] && [[ ${BIGCHAINDB_CI_ABCI} != 'enable' ]] && [[ ${BIGCHAINDB_ACCEPTANCE_TEST} != 'enable' ]]; then
    codecov -v -f htmlcov/coverage.xml
fi
