FROM openresty/openresty:alpine
RUN apk update \
    && apk upgrade \
    && apk add bash
COPY nginx.conf.template /etc/nginx/nginx.conf
COPY nginx_entrypoint.bash /
EXPOSE 443
ENTRYPOINT ["/nginx_entrypoint.bash"]
