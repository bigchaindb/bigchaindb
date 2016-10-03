FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

RUN apt-key adv --keyserver pgp.mit.edu --recv-keys 1614552E5765227AEC39EFCFA7E00EF33A8F2399
RUN echo "deb http://download.rethinkdb.com/apt xenial main" > /etc/apt/sources.list.d/rethinkdb.list

RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get -y install rethinkdb g++ python3 python3-pip && \
    pip3 install --upgrade pip setuptools && \
    apt-get -y auto-remove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src/app
COPY . /usr/src/app/
WORKDIR /usr/src/app
RUN pip3 install --no-cache-dir -e .

VOLUME ["/data"]
WORKDIR /data

ENV BIGCHAINDB_CONFIG_PATH /data/.bigchaindb
ENV BIGCHAINDB_SERVER_BIND 0.0.0.0:9984
ENV BIGCHAINDB_API_ENDPOINT http://bdb:9984/api/v1
ENV BIGCHAINDB_DATABASE_NAME: bigchaindb

EXPOSE 9984 28015 29015

COPY ./docker-start-rethink.sh /start.sh
RUN chmod a+x /start.sh

CMD ["/start.sh"]
