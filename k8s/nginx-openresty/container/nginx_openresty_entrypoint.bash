#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

set -euo pipefail

# Openresty vars
dns_server=`printenv DNS_SERVER`
openresty_frontend_port=`printenv OPENRESTY_FRONTEND_PORT`


# BigchainDB vars
bdb_backend_host=`printenv BIGCHAINDB_BACKEND_HOST`
bdb_api_port=`printenv BIGCHAINDB_API_PORT`


# Read the 3scale credentials from the mountpoint
# Should be mounted at the following directory
THREESCALE_CREDENTIALS_DIR=/usr/local/openresty/nginx/conf/threescale

threescale_secret_token=`cat ${THREESCALE_CREDENTIALS_DIR}/secret-token`
threescale_service_id=`cat ${THREESCALE_CREDENTIALS_DIR}/service-id`
threescale_version_header=`cat ${THREESCALE_CREDENTIALS_DIR}/version-header`
threescale_service_token=`cat ${THREESCALE_CREDENTIALS_DIR}/service-token`


if [[ -z "${dns_server:?DNS_SERVER not specified. Exiting!}" || \
    -z "${openresty_frontend_port:?OPENRESTY_FRONTEND_PORT not specified. Exiting!}" || \
    -z "${bdb_backend_host:?BIGCHAINDB_BACKEND_HOST not specified. Exiting!}" || \
    -z "${bdb_api_port:?BIGCHAINDB_API_PORT not specified. Exiting!}" || \
    -z "${threescale_secret_token:?3scale secret token not specified. Exiting!}" || \
    -z "${threescale_service_id:?3scale service id not specified. Exiting!}" || \
    -z "${threescale_version_header:?3scale version header not specified. Exiting!}" || \
    -z "${threescale_service_token:?3scale service token not specified. Exiting!}" ]]; then
  echo "Invalid environment settings detected. Exiting!"
  exit 1
fi

NGINX_LUA_FILE=/usr/local/openresty/nginx/conf/nginx.lua
NGINX_CONF_FILE=/usr/local/openresty/nginx/conf/nginx.conf

# configure the nginx.lua file with env variables
sed -i "s|SERVICE_ID|${threescale_service_id}|g" ${NGINX_LUA_FILE}
sed -i "s|THREESCALE_RESPONSE_SECRET_TOKEN|${threescale_secret_token}|g" ${NGINX_LUA_FILE}
sed -i "s|SERVICE_TOKEN|${threescale_service_token}|g" ${NGINX_LUA_FILE}

# configure the nginx.conf file with env variables
sed -i "s|DNS_SERVER|${dns_server}|g" ${NGINX_CONF_FILE}
sed -i "s|OPENRESTY_FRONTEND_PORT|${openresty_frontend_port}|g" ${NGINX_CONF_FILE}
sed -i "s|BIGCHAINDB_BACKEND_HOST|${bdb_backend_host}|g" ${NGINX_CONF_FILE}
sed -i "s|BIGCHAINDB_API_PORT|${bdb_api_port}|g" ${NGINX_CONF_FILE}
sed -i "s|THREESCALE_RESPONSE_SECRET_TOKEN|${threescale_secret_token}|g" $NGINX_CONF_FILE
sed -i "s|SERVICE_ID|${threescale_service_id}|g" $NGINX_CONF_FILE
sed -i "s|THREESCALE_VERSION_HEADER|${threescale_version_header}|g" $NGINX_CONF_FILE
sed -i "s|SERVICE_TOKEN|${threescale_service_token}|g" $NGINX_CONF_FILE


# start nginx
echo "INFO: starting nginx..."
exec /usr/local/openresty/nginx/sbin/nginx -c ${NGINX_CONF_FILE}
