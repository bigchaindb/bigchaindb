#!/bin/bash

docker build -t bigchaindb/nginx_https:1.1 .

docker push bigchaindb/nginx_https:1.1
