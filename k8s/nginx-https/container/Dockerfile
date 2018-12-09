FROM nginx:stable
LABEL maintainer "devs@bigchaindb.com"
WORKDIR /
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get autoremove \
    && apt-get clean
COPY nginx.conf.threescale.template /etc/nginx/nginx-threescale.conf
COPY nginx.conf.template /etc/nginx/nginx.conf
COPY nginx_entrypoint.bash /
EXPOSE 80 443 27017 9986 26656
ENTRYPOINT ["/nginx_entrypoint.bash"]
