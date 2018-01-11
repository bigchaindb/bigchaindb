#!/bin/bash

docker build -t bigchaindb/nginx_http:1.1 .

docker push bigchaindb/nginx_http:1.1

# For tendermint deployments
# docker build -t bigchaindb/nginx_https:unstable-tmt . -f Dockerfile-TMT
# docker push bigchaindb/nginx_https:unstable-tmt
