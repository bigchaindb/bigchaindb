#!/bin/bash

docker build -t bigchaindb/nginx-https-web-proxy:0.12 .

docker push bigchaindb/nginx-https-web-proxy:0.12
