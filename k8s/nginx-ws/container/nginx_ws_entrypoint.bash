#!/bin/bash
set -euo pipefail

bdb_backend_host=`printenv BIGCHAINDB_BACKEND_HOST`
bdb_ws_frontend_port=`printenv BIGCHAINDB_WS_FRONTEND_PORT`
bdb_ws_backend_port=`printenv BIGCHAINDB_WS_BACKEND_PORT`
dns_server=`printenv DNS_SERVER`

# sanity checks
if [[ -z "${bdb_backend_host}" || \
    -z "${bdb_ws_frontend_port}" || \
    -z "${bdb_ws_backend_port}" || \
    -z "${dns_server}" ]] ; then
  echo "Invalid environment settings detected. Exiting!"
  exit 1
fi

NGINX_CONF_FILE=/etc/nginx/nginx.conf

# configure the nginx.conf file with env variables
sed -i "s|BIGCHAINDB_BACKEND_HOST|${bdb_backend_host}|g" $NGINX_CONF_FILE
sed -i "s|BIGCHAINDB_WS_FRONTEND_PORT|${bdb_ws_frontend_port}|g" $NGINX_CONF_FILE
sed -i "s|BIGCHAINDB_WS_BACKEND_PORT|${bdb_ws_backend_port}|g" $NGINX_CONF_FILE
sed -i "s|DNS_SERVER|${dns_server}|g" $NGINX_CONF_FILE

# start nginx
echo "INFO: starting nginx..."
exec nginx -c /etc/nginx/nginx.conf
