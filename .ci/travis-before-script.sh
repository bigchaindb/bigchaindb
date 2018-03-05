#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    docker-compose -f docker-compose.tendermint.yml up -d bdb
fi
