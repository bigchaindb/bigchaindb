#!/bin/bash

set -e -x

if [[ "${TOXENV}" == *-rdb ]]; then
    rethinkdb --daemon
elif [[ "${TOXENV}" == *-mdb ]]; then
    echo 'Setting up mongodb'
    sudo tee -a /etc/mongod.conf <<EOF
    replication:
      replSetName: bigchain
    EOF
    sudo service mongodb restart
    sleep 15
fi
