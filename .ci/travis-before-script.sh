#!/bin/bash

set -e -x

if [[ "${TOXENV}" == *-rdb ]]; then
    rethinkdb --daemon
elif [[ "${TOXENV}" == *-mdb ]]; then
    echo "replSet = rs0" | sudo tee -a
    sudo service mongod restart
    sleep 15
fi
