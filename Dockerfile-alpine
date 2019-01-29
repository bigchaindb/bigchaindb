FROM alpine:latest
LABEL maintainer "devs@bigchaindb.com"
RUN mkdir -p /usr/src/app
COPY . /usr/src/app/
WORKDIR /usr/src/app
RUN apk --update add sudo \
    && apk --update add python3 openssl ca-certificates git\
    && apk --update add --virtual build-dependencies python3-dev \
        libffi-dev openssl-dev build-base \
    && apk add --no-cache libstdc++ \
    && pip3 install --upgrade pip cffi \
    && pip install -e .[dev] \
    && apk del build-dependencies \
    && rm -f /var/cache/apk/*
# When developing with Python in a docker container, we are using PYTHONBUFFERED
# to force stdin, stdout and stderr to be totally unbuffered and to capture logs/outputs
ENV PYTHONUNBUFFERED 0

ENV BIGCHAINDB_DATABASE_PORT 27017
ENV BIGCHAINDB_DATABASE_BACKEND $backend
ENV BIGCHAINDB_SERVER_BIND 0.0.0.0:9984
ENV BIGCHAINDB_WSSERVER_HOST 0.0.0.0
ENV BIGCHAINDB_WSSERVER_SCHEME ws

ENV BIGCHAINDB_WSSERVER_ADVERTISED_HOST 0.0.0.0
ENV BIGCHAINDB_WSSERVER_ADVERTISED_SCHEME ws

ENV BIGCHAINDB_TENDERMINT_PORT 26657
ARG backend
RUN bigchaindb -y configure "$backend"