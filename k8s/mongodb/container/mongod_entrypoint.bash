#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

set -euo pipefail

MONGODB_PORT=""
MONGODB_KEY_FILE_PATH=""
MONGODB_CA_FILE_PATH=""
MONGODB_CRL_FILE_PATH=""
MONGODB_FQDN=""
MONGODB_IP=""

# vars for MongoDB configuration
configure_mongo=true
MONGODB_CREDENTIALS_DIR=/tmp/mongodb
mongodb_admin_password=""
mongodb_admin_username=`printenv MONGODB_ADMIN_USERNAME || true`
bdb_username=`printenv BDB_USERNAME || true`
mdb_mon_username=`printenv MDB_MON_USERNAME || true`

while [[ $# -gt 1 ]]; do
    arg="$1"
    case $arg in
        --mongodb-port)
            MONGODB_PORT="$2"
            shift
        ;;
        --mongodb-key-file-path)
            MONGODB_KEY_FILE_PATH="$2"
            shift
        ;;
        --mongodb-ca-file-path)
            MONGODB_CA_FILE_PATH="$2"
            shift
        ;;
        --mongodb-crl-file-path)
            MONGODB_CRL_FILE_PATH="$2"
            shift
        ;;
        --mongodb-fqdn)
            MONGODB_FQDN="$2"
            shift
        ;;
        --mongodb-ip)
            MONGODB_IP="$2"
            shift
        ;;
        --storage-engine-cache-size)
            STORAGE_ENGINE_CACHE_SIZE="$2"
            shift
        ;;
        *)
            echo "Unknown option: $1"
            exit 1
        ;;
    esac
    shift
done

# sanity checks
if [[ -z "${MONGODB_PORT:?MONGODB_PORT not specified. Exiting!}" || \
        -z "${MONGODB_FQDN:?MONGODB_FQDN not specified. Exiting!}" || \
        -z "${MONGODB_IP:?MONGODB_IP not specified. Exiting!}" || \
        -z "${MONGODB_KEY_FILE_PATH:?MONGODB_KEY_FILE_PATH not specified. Exiting!}" || \
        -z "${MONGODB_CA_FILE_PATH:?MONGODB_CA_FILE_PATH not specified. Exiting!}" || \
    -z "${MONGODB_CRL_FILE_PATH:?MONGODB_CRL_FILE_PATH not specified. Exiting!}" ]] ; then
    # Not handling the STORAGE_ENGINE_CACHE_SIZE because
    # it is optional. If not specified the default cache
    # size is: max((50% RAM - 1GB), 256MB)
    exit 1
else
    echo MONGODB_PORT="$MONGODB_PORT"
    echo MONGODB_FQDN="$MONGODB_FQDN"
    echo MONGODB_IP="$MONGODB_IP"
    echo MONGODB_KEY_FILE_PATH="$MONGODB_KEY_FILE_PATH"
    echo MONGODB_CA_FILE_PATH="$MONGODB_CA_FILE_PATH"
    echo MONGODB_CRL_FILE_PATH="$MONGODB_CRL_FILE_PATH"
    echo STORAGE_ENGINE_CACHE_SIZE="$STORAGE_ENGINE_CACHE_SIZE"
fi

MONGODB_CONF_FILE_PATH=/etc/mongod.conf
HOSTS_FILE_PATH=/etc/hosts
MONGODB_CONFIGURE_USERS_PATH=/configure_mdb_users.js

# configure the mongod.conf file
sed -i "s|MONGODB_PORT|${MONGODB_PORT}|g" ${MONGODB_CONF_FILE_PATH}
sed -i "s|MONGODB_KEY_FILE_PATH|${MONGODB_KEY_FILE_PATH}|g" ${MONGODB_CONF_FILE_PATH}
sed -i "s|MONGODB_CA_FILE_PATH|${MONGODB_CA_FILE_PATH}|g" ${MONGODB_CONF_FILE_PATH}
sed -i "s|MONGODB_CRL_FILE_PATH|${MONGODB_CRL_FILE_PATH}|g" ${MONGODB_CONF_FILE_PATH}
if [ ! -z "$STORAGE_ENGINE_CACHE_SIZE" ]; then
    if [[ "$STORAGE_ENGINE_CACHE_SIZE" =~ ^[0-9]+(G|M|T)B$ ]]; then
        sed -i.bk "s|STORAGE_ENGINE_CACHE_SIZE|${STORAGE_ENGINE_CACHE_SIZE}|g" ${MONGODB_CONF_FILE_PATH}
    else
        echo "Invalid Value for storage engine cache size $STORAGE_ENGINE_CACHE_SIZE"
        exit 1
    fi
else
    sed -i.bk "/cache_size=/d" ${MONGODB_CONF_FILE_PATH}
fi

if [ -f ${MONGODB_CREDENTIALS_DIR}/mdb-admin-password ]; then
    mongodb_admin_password=`cat ${MONGODB_CREDENTIALS_DIR}/mdb-admin-password`
fi

# Only configure if all variables are set
if [[ -n "${mongodb_admin_username}" && \
        -n "${mongodb_admin_password}" ]]; then
    sed -i "s|MONGODB_ADMIN_USERNAME|${mongodb_admin_username}|g" ${MONGODB_CONFIGURE_USERS_PATH}
    sed -i "s|MONGODB_ADMIN_PASSWORD|${mongodb_admin_password}|g" ${MONGODB_CONFIGURE_USERS_PATH}
    sed -i "s|CONFIGURE_ADMIN_USER|true|g" ${MONGODB_CONFIGURE_USERS_PATH}
else
    sed -i "s|CONFIGURE_ADMIN_USER|false|g" ${MONGODB_CONFIGURE_USERS_PATH}
fi

if [[ -n "${bdb_username}" ]]; then
    sed -i "s|BDB_USERNAME|${bdb_username}|g" ${MONGODB_CONFIGURE_USERS_PATH}
    sed -i "s|CONFIGURE_BDB_USER|true|g" ${MONGODB_CONFIGURE_USERS_PATH}
else
    sed -i "s|CONFIGURE_BDB_USER|false|g" ${MONGODB_CONFIGURE_USERS_PATH}
fi

if [[ -n "${mdb_mon_username}" ]]; then
    sed -i "s|MDB_MON_USERNAME|${mdb_mon_username}|g" ${MONGODB_CONFIGURE_USERS_PATH}
    sed -i "s|CONFIGURE_MDB_MON_USER|true|g" ${MONGODB_CONFIGURE_USERS_PATH}
else
    sed -i "s|CONFIGURE_MDB_MON_USER|false|g" ${MONGODB_CONFIGURE_USERS_PATH}
fi

# add the hostname and ip to hosts file
echo "${MONGODB_IP} ${MONGODB_FQDN}" >> $HOSTS_FILE_PATH

# create the directory if it does not exist, where MongoDB can store the data
# and config files; this assumes that the data directory is mounted at
# /data/db/main and the config directory is mounted at /data/configdb
mkdir -p /data/db/main /data/configdb/main

# start mongod
echo "INFO: starting mongod..."

# TODO Uncomment the first exec command and use it instead of the second one
# after https://github.com/docker-library/mongo/issues/172 is resolved. Check
# for other bugs too.
#exec /entrypoint.sh mongod --config ${MONGODB_CONF_FILE_PATH}
exec /usr/bin/mongod --config ${MONGODB_CONF_FILE_PATH}
