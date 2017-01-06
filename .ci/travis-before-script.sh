#!/bin/bash

set -e -x

if [[ "${TOXENV}" == *-rdb ]]; then
    rethinkdb --daemon
elif [[ "${TOXENV}" == *-mdb ]]; then
    sudo tee -a /etc/mongod.conf <<EOF
    replication:
      replSetName: bigchain
    EOF
    sudo service mongod restart
    sleep 15
fi
