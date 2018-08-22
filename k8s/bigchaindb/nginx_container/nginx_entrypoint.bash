#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

set -euo pipefail

# Tendermint public key access port
tm_pub_key_access_port=`printenv TM_PUB_KEY_ACCESS_PORT`

if [[ -z "${tm_pub_key_access_port:?TM_PUB_KEY_ACCESS_PORT not specified. Exiting}" ]]; then
  exit 1
else
  echo TM_PUB_KEY_ACCESS_PORT="$tm_pub_key_access_port"
fi

NGINX_CONF_FILE=/etc/nginx/conf.d/access_pub_key.conf

# configure the access_pub_key file with env variable(s)
sed -i "s|PUBLIC_KEY_ACCESS_PORT|${tm_pub_key_access_port}|g" ${NGINX_CONF_FILE}

cat /etc/nginx/conf.d/access_pub_key.conf
# start nginx
echo "INFO: starting nginx..."
exec nginx -g "daemon off;"
