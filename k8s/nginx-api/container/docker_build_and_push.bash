#!/bin/bash

docker build -t bigchaindb/nginx_api:1.0 .

docker push bigchaindb/nginx_api:1.0
