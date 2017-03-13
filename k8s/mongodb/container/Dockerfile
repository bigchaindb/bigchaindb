FROM mongo:3.4.2
MAINTAINER dev@bigchaindb.com
WORKDIR /
COPY mongod.conf.template /etc/mongod.conf.template
COPY mongod_entrypoint/mongod_entrypoint /
RUN apt-get update && apt-get -y upgrade
VOLUME /data/db /data/configdb
EXPOSE 27017
ENTRYPOINT ["/mongod_entrypoint"]
