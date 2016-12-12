#!/bin/bash

if [ "${TOXENV}" == "py34" ] || [ "${TOXENV}" == "py35" ]; then
    source /etc/lsb-release
    echo "deb http://download.rethinkdb.com/apt $DISTRIB_CODENAME main" | tee -a /etc/apt/sources.list.d/rethinkdb.list
    wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | apt-key add -
    apt-get update -qq
fi
