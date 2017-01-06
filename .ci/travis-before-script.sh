#!/bin/bash

set -e -x

if [[ "${BIGCHAINDB_DATABASE_BACKEND}" == mongodb ]]; then
    sudo tee -a /etc/mongod.conf <<EOF
    replication:
      replSetName: bigchain
    EOF
    sudo service mongod restart
    sleep 15
fi
