FROM python:3.6
LABEL maintainer "dev@bigchaindb.com"

RUN apt-get update \
    && apt-get install -y vim \
    && pip install -U pip \
    && pip install pynacl \
    && apt-get autoremove \
    && apt-get clean

ARG backend

ENV PYTHONUNBUFFERED 0

ENV BIGCHAINDB_DATABASE_PORT 27017
ENV BIGCHAINDB_DATABASE_BACKEND $backend
ENV BIGCHAINDB_SERVER_BIND 0.0.0.0:9984
ENV BIGCHAINDB_WSSERVER_HOST 0.0.0.0
ENV BIGCHAINDB_WSSERVER_SCHEME ws

ENV BIGCHAINDB_WSSERVER_ADVERTISED_HOST 0.0.0.0
ENV BIGCHAINDB_WSSERVER_ADVERTISED_SCHEME ws

ENV BIGCHAINDB_START_TENDERMINT 0
ENV TENDERMINT_PORT 46657


RUN mkdir -p /usr/src/app
COPY . /usr/src/app/
WORKDIR /usr/src/app
RUN pip install --no-cache-dir -e .[dev]
RUN bigchaindb -y configure "$backend"
