#!/bin/bash

set -e -x

if [[ "${TOXENV}" == *-rdb ]]; then
    rethinkdb --daemon
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == mongodb && \
        -z "${BIGCHAINDB_DATABASE_SSL}" ]]; then
    # Connect to MongoDB on port 27017 via a normal, unsecure connection if
    # BIGCHAINDB_DATABASE_SSL is unset.
    # It is unset in this case in .travis.yml.
    wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-3.4.4.tgz -O /tmp/mongodb.tgz
    tar -xvf /tmp/mongodb.tgz
    mkdir /tmp/mongodb-data
    ${PWD}/mongodb-linux-x86_64-ubuntu1404-3.4.4/bin/mongod \
        --dbpath=/tmp/mongodb-data --replSet=bigchain-rs &> /dev/null &
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == mongodb && \
        "${BIGCHAINDB_DATABASE_SSL}" == true ]]; then
    # Connect to MongoDB on port 27017 via TLS/SSL connection if
    # BIGCHAINDB_DATABASE_SSL is set.
    # It is set to 'true' here in .travis.yml. Dummy certificates for testing
    # are stored under bigchaindb/tests/backend/mongodb-ssl/certs/ directory.
    wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-3.4.4.tgz -O /tmp/mongodb-ssl.tgz
    tar -xvf /tmp/mongodb-ssl.tgz
    mkdir /tmp/mongodb-ssl-data
    ${PWD}/mongodb-linux-x86_64-ubuntu1404-3.4.4/bin/mongod \
        --dbpath=/tmp/mongodb-ssl-data \
        --replSet=bigchain-rs \
        --sslAllowInvalidHostnames \
        --sslMode=requireSSL \
        --sslCAFile=$TRAVIS_BUILD_DIR/tests/backend/mongodb-ssl/certs/ca.crt \
        --sslCRLFile=$TRAVIS_BUILD_DIR/tests/backend/mongodb-ssl/certs/crl.pem \
        --sslPEMKeyFile=$TRAVIS_BUILD_DIR/tests/backend/mongodb-ssl/certs/test_mdb_ssl_cert_and_key.pem &> /dev/null &
fi
