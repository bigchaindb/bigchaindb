#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

set -euo pipefail

# Cluster vars
node_frontend_port=`printenv NODE_FRONTEND_PORT`


# NGINX vars
dns_server=`printenv DNS_SERVER`
health_check_port=`printenv HEALTH_CHECK_PORT`


# MongoDB vars
mongo_frontend_port=`printenv MONGODB_FRONTEND_PORT`
mongo_backend_host=`printenv MONGODB_BACKEND_HOST`
mongo_backend_port=`printenv MONGODB_BACKEND_PORT`


# BigchainDB vars
bdb_backend_host=`printenv BIGCHAINDB_BACKEND_HOST`
bdb_api_port=`printenv BIGCHAINDB_API_PORT`
bdb_ws_port=`printenv BIGCHAINDB_WS_PORT`

# Tendermint vars
tm_pub_key_access_port=`printenv TM_PUB_KEY_ACCESS_PORT`
tm_p2p_port=`printenv TM_P2P_PORT`


# sanity check
if [[ -z "${node_frontend_port:?NODE_FRONTEND_PORT not specified. Exiting!}" || \
      -z "${mongo_frontend_port:?MONGODB_FRONTEND_PORT not specified. Exiting!}" || \
      -z "${mongo_backend_host:?MONGODB_BACKEND_HOST not specified. Exiting!}" || \
      -z "${mongo_backend_port:?MONGODB_BACKEND_PORT not specified. Exiting!}" || \
      -z "${bdb_backend_host:?BIGCHAINDB_BACKEND_HOST not specified. Exiting!}" || \
      -z "${bdb_api_port:?BIGCHAINDB_API_PORT not specified. Exiting!}" || \
      -z "${bdb_ws_port:?BIGCHAINDB_WS_PORT not specified. Exiting!}" || \
      -z "${dns_server:?DNS_SERVER not specified. Exiting!}" || \
      -z "${health_check_port:?HEALTH_CHECK_PORT not specified.}" || \
      -z "${tm_pub_key_access_port:?TM_PUB_KEY_ACCESS_PORT not specified. Exiting!}" || \
      -z "${tm_p2p_port:?TM_P2P_PORT not specified. Exiting!}" ]]; then
  exit 1
else
  echo NODE_FRONTEND_PORT="$node_frontend_port"
  echo DNS_SERVER="$dns_server"
  echo HEALTH_CHECK_PORT="$health_check_port"
  echo MONGODB_FRONTEND_PORT="$mongo_frontend_port"
  echo MONGODB_BACKEND_HOST="$mongo_backend_host"
  echo MONGODB_BACKEND_PORT="$mongo_backend_port"
  echo BIGCHAINDB_BACKEND_HOST="$bdb_backend_host"
  echo BIGCHAINDB_API_PORT="$bdb_api_port"
  echo BIGCHAINDB_WS_PORT="$bdb_ws_port"
  echo TM_PUB_KEY_ACCESS_PORT="$tm_pub_key_access_port"
  echo TM_P2P_PORT="$tm_p2p_port"
fi

NGINX_CONF_FILE=/etc/nginx/nginx.conf

# configure the nginx.conf file with env variables
sed -i "s|NODE_FRONTEND_PORT|${node_frontend_port}|g" ${NGINX_CONF_FILE}
sed -i "s|MONGODB_FRONTEND_PORT|${mongo_frontend_port}|g" ${NGINX_CONF_FILE}
sed -i "s|MONGODB_BACKEND_HOST|${mongo_backend_host}|g" ${NGINX_CONF_FILE}
sed -i "s|MONGODB_BACKEND_PORT|${mongo_backend_port}|g" ${NGINX_CONF_FILE}
sed -i "s|BIGCHAINDB_BACKEND_HOST|${bdb_backend_host}|g" ${NGINX_CONF_FILE}
sed -i "s|BIGCHAINDB_API_PORT|${bdb_api_port}|g" ${NGINX_CONF_FILE}
sed -i "s|BIGCHAINDB_WS_PORT|${bdb_ws_port}|g" ${NGINX_CONF_FILE}
sed -i "s|DNS_SERVER|${dns_server}|g" ${NGINX_CONF_FILE}
sed -i "s|HEALTH_CHECK_PORT|${health_check_port}|g" ${NGINX_CONF_FILE}
sed -i "s|TM_PUB_KEY_ACCESS_PORT|${tm_pub_key_access_port}|g" ${NGINX_CONF_FILE}
sed -i "s|TM_P2P_PORT|${tm_p2p_port}|g" ${NGINX_CONF_FILE}

# start nginx
echo "INFO: starting nginx..."
exec nginx -c /etc/nginx/nginx.conf

