#!/bin/bash

set -e -x

pip install --upgrade pip

if [[ -n ${TOXENV} ]]; then
    pip install --upgrade tox
else
    docker-compose -f docker-compose.tendermint.yml build --no-cache
    pip install --upgrade codecov
fi
