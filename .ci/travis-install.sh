#!/bin/bash

set -e -x

pip install --upgrade pip

if [[ -n ${TOXENV} ]]; then
    pip install --upgrade tox
else
    docker-compose -f docker-compose.tendemrint.yml build --no-cache
    pip install --upgrade codecov
fi
