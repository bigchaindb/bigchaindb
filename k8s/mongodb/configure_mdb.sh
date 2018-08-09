#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


# Checking if kubectl exists
command -v kubectl > /dev/null
if [ $? -eq 0 ]
then
  echo "kubectl already installed!"
else
  echo "Please install kubectl!! https://kubernetes.io/docs/tasks/tools/install-kubectl/"
  exit 1
fi

MONGODB_INSTANCE_NAME="mdb-instance-0"

if [[ -n "$MONGODB_INSTANCE_NAME" ]]; then
    /usr/local/bin/kubectl exec -it "${MONGODB_INSTANCE_NAME}"\-ss\-0 -- bash -c "/usr/bin/mongo --host localhost --port \$(printenv MONGODB_PORT) --ssl --sslCAFile /etc/mongod/ca/ca.pem --sslPEMKeyFile  /etc/mongod/ssl/mdb-instance.pem < /configure_mdb_users.js"
else
    echo "Skipping configuration, because relevant files don't exist!!!"
fi
