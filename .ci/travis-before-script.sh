#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    docker-compose up -d bdb
fi
