#!/bin/bash

set -e -x

if [[ ${BIGCHAINDB_CI_ABCI} == 'enable' ]]; then
    sleep 3600
else
    bigchaindb -l DEBUG start
fi
