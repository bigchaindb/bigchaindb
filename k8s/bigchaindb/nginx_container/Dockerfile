FROM nginx:stable
LABEL maintainer "contact@ipdb.global"
WORKDIR /
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get autoremove \
    && apt-get clean
COPY nginx.conf.template /etc/nginx/conf.d/access_pub_key.conf
COPY nginx_entrypoint.bash /
VOLUME /usr/share/nginx
EXPOSE 9986
ENTRYPOINT ["/nginx_entrypoint.bash"]
