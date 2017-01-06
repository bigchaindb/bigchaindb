#!/bin/bash

set -e -x

echo 'running before script'
echo $TOXENV

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
