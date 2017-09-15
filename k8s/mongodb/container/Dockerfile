FROM mongo:3.4.4
LABEL maintainer "dev@bigchaindb.com"
WORKDIR /
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get autoremove \
    && apt-get clean
COPY mongod.conf.template /etc/mongod.conf
COPY mongod_entrypoint.bash /
VOLUME /data/db /data/configdb /etc/mongod/ssl /etc/mongod/ca
EXPOSE 27017
ENTRYPOINT ["/mongod_entrypoint.bash"]
