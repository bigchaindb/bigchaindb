FROM python:3.6
LABEL maintainer "dev@bigchaindb.com"

RUN apt-get update \
    && pip install -U pip \
    && apt-get autoremove \
    && apt-get clean

ARG backend

ENV PYTHONUNBUFFERED 0

ENV BIGCHAINDB_DATABASE_PORT 27017
ENV BIGCHAINDB_DATABASE_BACKEND $backend
ENV BIGCHAINDB_WSSERVER_SCHEME ws
ENV BIGCHAINDB_WSSERVER_ADVERTISED_SCHEME ws

ENV BIGCHAINDB_START_TENDERMINT 0
ENV BIGCHAINDB_TENDERMINT_PORT 46657

RUN mkdir -p /usr/src/app
COPY . /usr/src/app/
WORKDIR /usr/src/app
RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
RUN pip install --no-cache-dir .[test]
RUN bigchaindb -y configure "$backend"
