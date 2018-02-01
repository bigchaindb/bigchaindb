#!/bin/bash

docker build -t bigchaindb/nginx_http:unstable-tmt .

docker push bigchaindb/nginx_http:unstable-tmt
