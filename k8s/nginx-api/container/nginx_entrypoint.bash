#!/bin/bash
set -euo pipefail

mongo_frontend_port=`printenv MONGODB_FRONTEND_PORT`
mongo_backend_host=`printenv MONGODB_BACKEND_HOST`
mongo_backend_port=`printenv MONGODB_BACKEND_PORT`
bdb_frontend_port=`printenv BIGCHAINDB_FRONTEND_PORT`
bdb_backend_host=`printenv BIGCHAINDB_BACKEND_HOST`
bdb_backend_port=`printenv BIGCHAINDB_BACKEND_PORT`
dns_server=`printenv DNS_SERVER`

# sanity checks
if [[ -z "${mongo_frontend_port}" || \
    -z "${mongo_backend_host}" || \
    -z "${mongo_backend_port}" || \
    -z "${bdb_frontend_port}" || \
    -z "${bdb_backend_host}" || \
    -z "${bdb_backend_port}" || \
    -z "${dns_server}" ]] ; then
  echo "Invalid environment settings detected. Exiting!"
  exit 1
fi

NGINX_CONF_FILE=/etc/nginx/nginx.conf

# configure the nginx.conf file with env variables
sed -i "s|MONGODB_FRONTEND_PORT|${mongo_frontend_port}|g" $NGINX_CONF_FILE
sed -i "s|MONGODB_BACKEND_HOST|${mongo_backend_host}|g" $NGINX_CONF_FILE
sed -i "s|MONGODB_BACKEND_PORT|${mongo_backend_port}|g" $NGINX_CONF_FILE
sed -i "s|BIGCHAINDB_FRONTEND_PORT|${bdb_frontend_port}|g" $NGINX_CONF_FILE
sed -i "s|BIGCHAINDB_BACKEND_HOST|${bdb_backend_host}|g" $NGINX_CONF_FILE
sed -i "s|BIGCHAINDB_BACKEND_PORT|${bdb_backend_port}|g" $NGINX_CONF_FILE
sed -i "s|DNS_SERVER|${dns_server}|g" $NGINX_CONF_FILE

# start nginx
echo "INFO: starting nginx..."
exec nginx -c /etc/nginx/nginx.conf
