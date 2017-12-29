FROM registry.access.redhat.com/3scale-amp20/apicast-gateway
LABEL maintainer "dev@bigchaindb.com"

COPY nginx.conf.template /opt/app-root/src/sites.d/nginx.conf
COPY nginx.lua.template /opt/app-root/src/sites.d/nginx.lua
COPY config.json /opt/app-root/src/conf/config.json
COPY nginx_openresty_entrypoint.bash /opt/app-root/scripts/

ENV THREESCALE_CONFIG_FILE "/opt/app-root/src/conf/config.json"
# The following ports are the values we use to run the NGINX+3scale container.
# 80 for http, 8080 for the 3scale api, 8888 for health-check, 27017 for
# MongoDB
EXPOSE 80 8080 8888 27017
ENTRYPOINT ["/nginx_openresty_entrypoint.bash"]
