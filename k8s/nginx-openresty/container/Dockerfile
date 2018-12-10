FROM openresty/openresty:xenial
LABEL maintainer "devs@bigchaindb.com"
WORKDIR /
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get autoremove \
    && apt-get clean
COPY nginx.conf.template /usr/local/openresty/nginx/conf/nginx.conf
COPY nginx.lua.template /usr/local/openresty/nginx/conf/nginx.lua
COPY nginx_openresty_entrypoint.bash /
# The following ports are the values we use to run the NGINX+3scale container.
# 80 for http, 8080 for the 3scale api, 8888 for health-check, 27017 for
# MongoDB
EXPOSE 80 8080 8888 27017
ENTRYPOINT ["/nginx_openresty_entrypoint.bash"]
