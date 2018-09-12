FROM openresty/openresty:xenial
LABEL maintainer "dev@bigchaindb.com"
WORKDIR /opt/apicast
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get autoremove \
    && apt-get clean \
    && apt-get install wget
COPY nginx_openresty_entrypoint.bash /

# The following ports are the values we use to run the NGINX+3scale container.
# 80 for http, 8080 for the 3scale api, 8888 for health-check, 27017 for
# MongoDB
EXPOSE 8080 8090 8888

ENTRYPOINT ["/nginx_openresty_entrypoint.bash"]