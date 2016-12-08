#!/bin/bash

set -e -x

if [ "${TOXENV}" == *-rdb ]; then
    rethinkdb --daemon
elif [ "${TOXENV}" == *-mdb ]; then
    service mongod start
fi
