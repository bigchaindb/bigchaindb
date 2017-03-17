FROM ubuntu:xenial

ENV LANG en_US.UTF-8
ENV DEBIAN_FRONTEND noninteractive

RUN mkdir -p /usr/src/app
COPY . /usr/src/app/
WORKDIR /usr/src/app

RUN locale-gen en_US.UTF-8 && \
    apt-get -q update && \
    apt-get install -qy --no-install-recommends \
        python3 \
        python3-pip \
        libffi-dev \
        python3-dev \
        build-essential && \
    \
    pip3 install --upgrade --no-cache-dir pip setuptools && \
    \
    pip3 install --no-cache-dir -e . && \
    \
    apt-get remove -qy --purge gcc cpp binutils perl && \
    apt-get -qy autoremove && \
    apt-get -q clean all && \
    rm -rf /usr/share/perl /usr/share/perl5 /usr/share/man /usr/share/info /usr/share/doc && \
    rm -rf /var/lib/apt/lists/*

VOLUME ["/data"]
WORKDIR /data

ENV BIGCHAINDB_CONFIG_PATH /data/.bigchaindb
ENV BIGCHAINDB_SERVER_BIND 0.0.0.0:9984
# BigchainDB Server doesn't need BIGCHAINDB_API_ENDPOINT any more
# but maybe our Docker or Docker Compose stuff does?
# ENV BIGCHAINDB_API_ENDPOINT http://bigchaindb:9984/api/v1

ENTRYPOINT ["bigchaindb"]

CMD ["start"]
