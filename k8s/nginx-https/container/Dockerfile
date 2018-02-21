FROM nginx:stable
LABEL maintainer "dev@bigchaindb.com"
WORKDIR /
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get autoremove \
    && apt-get clean
COPY nginx.conf.tmt.template /etc/nginx/nginx.conf
COPY nginx_tmt_entrypoint.bash /
EXPOSE 80 443 27017 9986 46656
ENTRYPOINT ["/nginx_tmt_entrypoint.bash"]
