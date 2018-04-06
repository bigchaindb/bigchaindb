#!/bin/bash

docker build -t bigchaindb/nginx_https:2.0.0-alpha .

docker push bigchaindb/nginx_https:2.0.0-alpha
