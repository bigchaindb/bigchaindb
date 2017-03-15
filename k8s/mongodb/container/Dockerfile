FROM mongo:3.4.2
LABEL maintainer "dev@bigchaindb.com"
WORKDIR /
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get autoremove \
    && apt-get clean
COPY mongod.conf.template /etc/mongod.conf.template
COPY mongod_entrypoint/mongod_entrypoint /
VOLUME /data/db /data/configdb
EXPOSE 27017
ENTRYPOINT ["/mongod_entrypoint"]
