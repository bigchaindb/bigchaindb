#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


set -e -x

if [[ -z ${TOXENV} ]] && [[ ${BIGCHAINDB_CI_ABCI} != 'enable' ]] && [[ ${BIGCHAINDB_ACCEPTANCE_TEST} != 'enable' ]]; then
    codecov -v -f htmlcov/coverage.xml
fi
