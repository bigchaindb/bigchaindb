#!/bin/bash
set -euo pipefail

# Cluster vars
cluster_fqdn=`printenv CLUSTER_FQDN`
cluster_frontend_port=`printenv CLUSTER_FRONTEND_PORT`


# NGINX vars
dns_server=`printenv DNS_SERVER`
health_check_port=`printenv HEALTH_CHECK_PORT`


# MongoDB vars
mongo_frontend_port=`printenv MONGODB_FRONTEND_PORT`
mongo_backend_host=`printenv MONGODB_BACKEND_HOST`
mongo_backend_port=`printenv MONGODB_BACKEND_PORT`


# OpenResty vars
openresty_backend_host=`printenv OPENRESTY_BACKEND_HOST`
openresty_backend_port=`printenv OPENRESTY_BACKEND_PORT`


# BigchainDB vars
bdb_backend_host=`printenv BIGCHAINDB_BACKEND_HOST`
bdb_api_port=`printenv BIGCHAINDB_API_PORT`
bdb_ws_port=`printenv BIGCHAINDB_WS_PORT`


# sanity check
if [[ -z "${cluster_frontend_port}" || \
      -z "${mongo_frontend_port}" || \
      -z "${mongo_backend_host}" || \
      -z "${mongo_backend_port}" || \
      -z "${openresty_backend_port}" || \
      -z "${openresty_backend_host}" || \
      -z "${bdb_backend_host}" || \
      -z "${bdb_api_port}" || \
      -z "${bdb_ws_port}" || \
      -z "${dns_server}" || \
      -z "${health_check_port}" || \
      -z "${cluster_fqdn}" ]]; then
  echo "Invalid environment settings detected. Exiting!"
  exit 1
fi

NGINX_CONF_FILE=/etc/nginx/nginx.conf

# configure the nginx.conf file with env variables
sed -i "s|CLUSTER_FQDN|${cluster_fqdn}|g" ${NGINX_CONF_FILE}
sed -i "s|CLUSTER_FRONTEND_PORT|${cluster_frontend_port}|g" ${NGINX_CONF_FILE}
sed -i "s|MONGODB_FRONTEND_PORT|${mongo_frontend_port}|g" ${NGINX_CONF_FILE}
sed -i "s|MONGODB_BACKEND_HOST|${mongo_backend_host}|g" ${NGINX_CONF_FILE}
sed -i "s|MONGODB_BACKEND_PORT|${mongo_backend_port}|g" ${NGINX_CONF_FILE}
sed -i "s|OPENRESTY_BACKEND_PORT|${openresty_backend_port}|g" ${NGINX_CONF_FILE}
sed -i "s|OPENRESTY_BACKEND_HOST|${openresty_backend_host}|g" ${NGINX_CONF_FILE}
sed -i "s|BIGCHAINDB_BACKEND_HOST|${bdb_backend_host}|g" ${NGINX_CONF_FILE}
sed -i "s|BIGCHAINDB_API_PORT|${bdb_api_port}|g" ${NGINX_CONF_FILE}
sed -i "s|BIGCHAINDB_WS_PORT|${bdb_ws_port}|g" ${NGINX_CONF_FILE}
sed -i "s|DNS_SERVER|${dns_server}|g" ${NGINX_CONF_FILE}
sed -i "s|HEALTH_CHECK_PORT|${health_check_port}|g" ${NGINX_CONF_FILE}

# start nginx
echo "INFO: starting nginx..."
exec nginx -c /etc/nginx/nginx.conf

