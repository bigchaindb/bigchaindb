FROM ubuntu:xenial
LABEL maintainer "dev@bigchaindb.com"
ARG DEBIAN_FRONTEND=noninteractive
ARG DEB_FILE=mongodb-mms-backup-agent_latest_amd64.ubuntu1604.deb
ARG FILE_URL="https://cloud.mongodb.com/download/agent/backup/"$DEB_FILE
WORKDIR /
RUN apt update \
    && apt -y upgrade \
    && apt -y install --no-install-recommends \
      curl \
      ca-certificates \
      logrotate \
      libsasl2-2 \
    && curl -OL $FILE_URL \
    && dpkg -i $DEB_FILE \
    && rm -f $DEB_FILE \
    && apt -y purge curl \
    && apt -y autoremove \
    && apt clean
COPY mongodb_backup_agent_entrypoint.bash /
RUN chown -R mongodb-mms-agent:mongodb-mms-agent /etc/mongodb-mms/
VOLUME /etc/mongod/ssl /etc/mongod/ca
USER mongodb-mms-agent
ENTRYPOINT ["/mongodb_backup_agent_entrypoint.bash"]
