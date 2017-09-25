#!/bin/bash

docker build -t bigchaindb/nginx_3scale:3.1 .

docker push bigchaindb/nginx_3scale:3.1
