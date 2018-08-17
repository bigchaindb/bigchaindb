#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

set -euo pipefail

# Proxy vars
proxy_fqdn=`printenv PROXY_FQDN`
proxy_frontend_port=`printenv PROXY_FRONTEND_PORT`

proxy_app_id_file=/etc/nginx/proxy/credentials/app_id
proxy_app_key_file=/etc/nginx/proxy/credentials/app_key
proxy_app_id=`cat ${proxy_app_id_file}`
proxy_app_key=`cat ${proxy_app_key_file}`

proxy_expected_referer_header=`printenv PROXY_EXPECTED_REFERER_HEADER`
proxy_expected_origin_header=`printenv PROXY_EXPECTED_ORIGIN_HEADER`

# OpenResty vars
openresty_backend_host=`printenv OPENRESTY_BACKEND_HOST`
openresty_backend_port=`printenv OPENRESTY_BACKEND_PORT`

# NGINX vars
dns_server=`printenv DNS_SERVER`
health_check_port=`printenv HEALTH_CHECK_PORT`

# BigchainDB vars
bdb_backend_host=`printenv BIGCHAINDB_BACKEND_HOST`
bdb_api_port=`printenv BIGCHAINDB_API_PORT`


# sanity check
if [[ -z "${proxy_frontend_port:?PROXY_FRONTEND_PORT not specified. Exiting!}" || \
      -z "${openresty_backend_port:?OPENRESTY_BACKEND_PORT not specified. Exiting!}" || \
      -z "${openresty_backend_host:?OPENRESTY_BACKEND_HOST not specified. Exiting!}" || \
      -z "${bdb_backend_host:?BIGCHAINDB_BACKEND_HOST not specified. Exiting!}" || \
      -z "${bdb_api_port:?BIGCHAINDB_API_PORT not specified. Exiting!}" || \
      -z "${dns_server:?DNS_SERVER not specified. Exiting!}" || \
      -z "${health_check_port:?HEALTH_CHECK_PORT not specified. Exiting!}" || \
      -z "${proxy_app_id:?PROXY_APP_ID not specified. Exiting!}" || \
      -z "${proxy_app_key:?PROXY_APP_KEY not specified. Exiting!}" || \
      -z "${proxy_expected_referer_header:?PROXY_EXPECTED_REFERER_HEADER not specified. Exiting!}" || \
      -z "${proxy_expected_origin_header:?PROXY_EXPECTED_ORIGIN_HEADER not specified. Exiting!}" || \
      -z "${proxy_fqdn:?PROXY_FQDN not specified. Exiting!}" ]]; then
  exit 1
else
  echo PROXY_FQDN="$proxy_fqdn"
  echo PROXY_FRONTEND_PORT="$proxy_frontend_port"
  echo PROXY_EXPECTED_REFERER_HEADER="$proxy_expected_referer_header"
  echo PROXY_EXPECTED_ORIGIN_HEADER="$proxy_expected_origin_header"
  echo DNS_SERVER="$dns_server"
  echo HEALTH_CHECK_PORT="$health_check_port"
  echo OPENRESTY_BACKEND_HOST="$openresty_backend_host"
  echo OPENRESTY_BACKEND_PORT="$openresty_backend_port"
  echo BIGCHAINDB_BACKEND_HOST="$bdb_backend_host"
  echo BIGCHAINDB_API_PORT="$bdb_api_port"
fi

NGINX_CONF_FILE=/etc/nginx/nginx.conf

# configure the nginx.conf file with env variables
sed -i "s|PROXY_FQDN|${proxy_fqdn}|g" ${NGINX_CONF_FILE}
sed -i "s|PROXY_FRONTEND_PORT|${proxy_frontend_port}|g" ${NGINX_CONF_FILE}
sed -i "s|OPENRESTY_BACKEND_PORT|${openresty_backend_port}|g" ${NGINX_CONF_FILE}
sed -i "s|OPENRESTY_BACKEND_HOST|${openresty_backend_host}|g" ${NGINX_CONF_FILE}
sed -i "s|BIGCHAINDB_BACKEND_HOST|${bdb_backend_host}|g" ${NGINX_CONF_FILE}
sed -i "s|BIGCHAINDB_API_PORT|${bdb_api_port}|g" ${NGINX_CONF_FILE}
sed -i "s|DNS_SERVER|${dns_server}|g" ${NGINX_CONF_FILE}
sed -i "s|HEALTH_CHECK_PORT|${health_check_port}|g" ${NGINX_CONF_FILE}
sed -i "s|PROXY_APP_ID|${proxy_app_id}|g" ${NGINX_CONF_FILE}
sed -i "s|PROXY_APP_KEY|${proxy_app_key}|g" ${NGINX_CONF_FILE}
sed -i "s|PROXY_EXPECTED_REFERER_HEADER|${proxy_expected_referer_header}|g" ${NGINX_CONF_FILE}
sed -i "s|PROXY_EXPECTED_ORIGIN_HEADER|${proxy_expected_origin_header}|g" ${NGINX_CONF_FILE}

# start nginx
echo "INFO: starting nginx..."
exec nginx -c /etc/nginx/nginx.conf
