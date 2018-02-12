#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    docker-compose -f docker-compose.travis.yml up -d bdb
fi
