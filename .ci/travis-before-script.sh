#!/bin/bash

set -e -x

if [[ "${BIGCHAINDB_DATABASE_BACKEND}" == localmongodb && \
        -z "${BIGCHAINDB_DATABASE_SSL}" ]]; then
    # Connect to MongoDB on port 27017 via a normal, unsecure connection if
    # BIGCHAINDB_DATABASE_SSL is unset.
    # It is unset in this case in .travis.yml.
    docker pull mongo:3.4
    docker run -d --publish=27017:27017 --name mdb-without-ssl mongo:3.4 # --replSet=bigchain-rs
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == localmongodb && \
        "${BIGCHAINDB_DATABASE_SSL}" == true ]]; then
    # Connect to MongoDB on port 27017 via TLS/SSL connection if
    # BIGCHAINDB_DATABASE_SSL is set.
    # It is set to 'true' here in .travis.yml. Dummy certificates for testing
    # are stored under bigchaindb/tests/backend/mongodb-ssl/certs/ directory.
    docker pull mongo:3.4
    docker run -d \
        --name mdb-with-ssl \
        --publish=27017:27017 \
        --volume=${TRAVIS_BUILD_DIR}/tests/backend/mongodb-ssl/certs:/certs \
        mongo:3.4 \
        --sslMode=requireSSL \
        --sslCAFile=/certs/ca-chain.cert.pem \
        --sslCRLFile=/certs/crl.pem \
        --sslPEMKeyFile=/certs/local-mongo.pem
fi
