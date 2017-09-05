#!/bin/bash

docker build -t bigchaindb/nginx-https-web-proxy:0.10 .

docker push bigchaindb/nginx-https-web-proxy:0.10
