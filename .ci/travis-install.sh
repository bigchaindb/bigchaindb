#!/bin/bash

set -e -x

pip install --upgrade pip

if [[ -n ${TOXENV} ]]; then
    pip install --upgrade tox
elif [[ ${BIGCHAINDB_CI_ABCI} == 'enable' ]]; then
    docker-compose build --no-cache --build-arg abci_status=enable bigchaindb
    pip install --upgrade codecov
else
    docker-compose build --no-cache bigchaindb
    pip install --upgrade codecov
fi
