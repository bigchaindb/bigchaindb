#!/bin/bash

docker build -t bigchaindb/nginx_http:unstable .

docker push bigchaindb/nginx_http:unstable
