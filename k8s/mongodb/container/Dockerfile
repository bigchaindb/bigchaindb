FROM mongo:3.4.13
LABEL maintainer "dev@bigchaindb.com"
WORKDIR /
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get autoremove \
    && apt-get clean
COPY mongod.conf.tmt.template /etc/mongod.conf
COPY mongod_tmt_entrypoint.bash /
VOLUME /data/db /data/configdb /etc/mongod/ssl /etc/mongod/ca
EXPOSE 27017
ENTRYPOINT ["/mongod_tmt_entrypoint.bash"]
