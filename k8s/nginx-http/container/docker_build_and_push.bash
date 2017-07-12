#!/bin/bash

docker build -t bigchaindb/nginx_http:1.0 .

docker push bigchaindb/nginx_http:1.0
