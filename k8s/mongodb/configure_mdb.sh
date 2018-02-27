#!/bin/bash

# Checking if kubectl exists
command -v kubectl > /dev/null
if [ $? -eq 0 ]
then
  echo "kubectl already installed!"
else
  echo "Please install kubectl!! https://kubernetes.io/docs/tasks/tools/install-kubectl/"
  exit 1
fi

[ -z $1 ] && echo "Please specify MongoDB instance name!!"
MONGODB_INSTANCE_NAME=$1

if [[ -n "$MONGODB_INSTANCE_NAME" ]]; then
    /usr/local/bin/kubectl exec -it "${MONGODB_INSTANCE_NAME}"\-ss\-0 -- bash -c "if [[ -f /tmp/configure_mongo && -n \$(cat /tmp/configure_mongo) ]]; then  /usr/bin/mongo --host localhost --port \$(printenv MONGODB_PORT) --ssl --sslCAFile /etc/mongod/ca/ca.pem --sslPEMKeyFile  /etc/mongod/ssl/mdb-instance.pem < /configure_mdb_users.js; fi"
else
    echo "Skipping configuration, because relevant files don't exist!!!"
fi
