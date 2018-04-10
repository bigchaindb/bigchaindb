#!/bin/bash

set -e -x

pip install --upgrade pip

if [[ -n ${TOXENV} ]]; then
    pip install --upgrade tox
elif [[ ${BIGCHAINDB_CI_ABCI} == 'enable' ]]; then
    docker-compose build --no-cache --build-arg abci_status=enable bigchaindb
elif [[ $TRAVIS_PYTHON_VERSION == 3.5 ]]; then
    docker-compose build --build-arg python_version=3.5 --no-cache bigchaindb
    pip install --upgrade codecov
else
    docker-compose build --no-cache bigchaindb
    pip install --upgrade codecov
fi
