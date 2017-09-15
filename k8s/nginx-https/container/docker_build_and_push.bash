#!/bin/bash

docker build -t bigchaindb/nginx_https:1.0 .

docker push bigchaindb/nginx_https:1.0
