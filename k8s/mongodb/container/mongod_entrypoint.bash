#!/bin/bash
set -euo pipefail

MONGODB_PORT=""
MONGODB_KEY_FILE_PATH=""
#MONGODB_KEY_FILE_PASSWORD=""
MONGODB_CA_FILE_PATH=""
MONGODB_CRL_FILE_PATH=""
REPLICA_SET_NAME=""
MONGODB_FQDN=""
MONGODB_IP=""

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
      --mongodb-key-file-password)
          # TODO(Krish) move this to a mapped file later
          MONGODB_KEY_FILE_PASSWORD="$2"
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
      --replica-set-name)
          REPLICA_SET_NAME="$2"
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
      *)
          echo "Unknown option: $1"
          exit 1
          ;;
  esac
  shift
done

# sanity checks
if [[ -z "${REPLICA_SET_NAME:?REPLICA_SET_NAME not specified. Exiting!}" || \
    -z "${MONGODB_PORT:?MONGODB_PORT not specified. Exiting!}" || \
    -z "${MONGODB_FQDN:?MONGODB_FQDN not specified. Exiting!}" || \
    -z "${MONGODB_IP:?MONGODB_IP not specified. Exiting!}" || \
    -z "${MONGODB_KEY_FILE_PATH:?MONGODB_KEY_FILE_PATH not specified. Exiting!}" || \
    -z "${MONGODB_CA_FILE_PATH:?MONGODB_CA_FILE_PATH not specified. Exiting!}" || \
    -z "${MONGODB_CRL_FILE_PATH:?MONGODB_CRL_FILE_PATH not specified. Exiting!}" ]] ; then
    #-z "${MONGODB_KEY_FILE_PASSWORD:?MongoDB Key File Password not specified. Exiting!}" || \
  exit 1
else
  echo REPLICA_SET_NAME="$REPLICA_SET_NAME"
  echo MONGODB_PORT="$MONGODB_PORT"
  echo MONGODB_FQDN="$MONGODB_FQDN"
  echo MONGODB_IP="$MONGODB_IP"
  echo MONGODB_KEY_FILE_PATH="$MONGODB_KEY_FILE_PATH"
  echo MONGODB_CA_FILE_PATH="$MONGODB_CA_FILE_PATH"
  echo MONGODB_CRL_FILE_PATH="$MONGODB_CRL_FILE_PATH"
fi

MONGODB_CONF_FILE_PATH=/etc/mongod.conf
HOSTS_FILE_PATH=/etc/hosts

# configure the mongod.conf file
sed -i "s|MONGODB_PORT|${MONGODB_PORT}|g" ${MONGODB_CONF_FILE_PATH}
sed -i "s|MONGODB_KEY_FILE_PATH|${MONGODB_KEY_FILE_PATH}|g" ${MONGODB_CONF_FILE_PATH}
#sed -i "s|MONGODB_KEY_FILE_PASSWORD|${MONGODB_KEY_FILE_PASSWORD}|g" ${MONGODB_CONF_FILE_PATH}
sed -i "s|MONGODB_CA_FILE_PATH|${MONGODB_CA_FILE_PATH}|g" ${MONGODB_CONF_FILE_PATH}
sed -i "s|MONGODB_CRL_FILE_PATH|${MONGODB_CRL_FILE_PATH}|g" ${MONGODB_CONF_FILE_PATH}
sed -i "s|REPLICA_SET_NAME|${REPLICA_SET_NAME}|g" ${MONGODB_CONF_FILE_PATH}

# add the hostname and ip to hosts file
echo "${MONGODB_IP} ${MONGODB_FQDN}" >> $HOSTS_FILE_PATH

# start mongod
echo "INFO: starting mongod..."

# TODO Uncomment the first exec command and use it instead of the second one
# after https://github.com/docker-library/mongo/issues/172 is resolved. Check
# for other bugs too.
#exec /entrypoint.sh mongod --config ${MONGODB_CONF_FILE_PATH}
exec /usr/bin/mongod --config ${MONGODB_CONF_FILE_PATH}
