#!/bin/bash

docker build -t bigchaindb/nginx_http:2.0.0-alpha5 .

docker push bigchaindb/nginx_http:2.0.0-alpha5
