#!/bin/bash

docker build -t bigchaindb/nginx_http:2.0.0-alpha3 .

docker push bigchaindb/nginx_http:2.0.0-alpha3
