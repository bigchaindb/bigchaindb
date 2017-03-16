#!/bin/bash

# constants
NGINX_CONF_FILE=/etc/nginx/nginx.conf

# configure the nginx.conf file with env variables
sed -i "s|MONGODB_FRONTEND_PORT|${MONGODB_FRONTEND_PORT}|g" $NGINX_CONF_FILE
sed -i "s|MONGODB_BACKEND_HOST|${MONGODB_BACKEND_HOST}|g" $NGINX_CONF_FILE
sed -i "s|MONGODB_BACKEND_PORT|${MONGODB_BACKEND_PORT}|g" $NGINX_CONF_FILE

sed -i "s|BIGCHAINDB_FRONTEND_PORT|${BIGCHAINDB_FRONTEND_PORT}|g" $NGINX_CONF_FILE
sed -i "s|BIGCHAINDB_BACKEND_HOST|${BIGCHAINDB_BACKEND_HOST}|g" $NGINX_CONF_FILE
sed -i "s|BIGCHAINDB_BACKEND_PORT|${BIGCHAINDB_BACKEND_PORT}|g" $NGINX_CONF_FILE

# populate the whitelist in the conf file as per MONGODB_WHITELIST env var
hosts=$(echo ${MONGODB_WHITELIST} | tr ":" "\n")
for host in $hosts; do
  sed -i "s|MONGODB_WHITELIST|allow ${host};\n    MONGODB_WHITELIST|g" $NGINX_CONF_FILE
done

# remove the MONGODB_WHITELIST marker from template
sed -i "s|MONGODB_WHITELIST||g" $NGINX_CONF_FILE

# start nginx
echo "INFO: starting nginx..."
nginx -c /etc/nginx/nginx.conf
echo "ERR: nginx dead!"
