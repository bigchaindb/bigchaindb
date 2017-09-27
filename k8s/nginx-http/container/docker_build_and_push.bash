#!/bin/bash

docker build -t bigchaindb/nginx_http:1.1 .

docker push bigchaindb/nginx_http:1.1
