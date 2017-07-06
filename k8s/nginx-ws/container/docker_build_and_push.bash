#!/bin/bash

docker build -t bigchaindb/nginx_ws:1.0 .

docker push bigchaindb/nginx_ws:1.0
