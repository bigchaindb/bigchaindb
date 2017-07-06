FROM nginx:1.13.1
LABEL maintainer "dev@bigchaindb.com"
WORKDIR /
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get autoremove \
    && apt-get clean
COPY nginx_ws.conf.template /etc/nginx/nginx.conf
COPY nginx_ws_entrypoint.bash /
EXPOSE 81 444 9985
ENTRYPOINT ["/nginx_ws_entrypoint.bash"]
