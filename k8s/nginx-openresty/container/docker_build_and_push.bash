#!/bin/bash

docker build -t bigchaindb/nginx_3scale:3.0 .

docker push bigchaindb/nginx_3scale:3.0
