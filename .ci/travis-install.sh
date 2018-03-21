#!/bin/bash

set -e -x

pip install --upgrade pip

if [[ -n ${TOXENV} ]]; then
    pip install --upgrade tox
else
    docker-compose build --no-cache bigchaindb
    pip install --upgrade codecov
fi
