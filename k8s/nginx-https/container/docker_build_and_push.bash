#!/bin/bash

docker build -t bigchaindb/nginx_https:2.0.0-alpha3 .

docker push bigchaindb/nginx_https:2.0.0-alpha3
