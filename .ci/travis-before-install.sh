#!/bin/bash

if [ "${TOXENV}" == *-rdb ]; then
    source /etc/lsb-release
    echo "deb http://download.rethinkdb.com/apt $DISTRIB_CODENAME main" | tee -a /etc/apt/sources.list.d/rethinkdb.list
    wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | apt-key add -
    apt-get update -qq
elif [ "${TOXENV}" == *-mdb ]; then
    source /etc/lsb-release
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
    echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.4.list
    apt-get update -qq
fi
