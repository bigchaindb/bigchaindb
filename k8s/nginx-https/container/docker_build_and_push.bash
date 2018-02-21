#!/bin/bash

docker build -t bigchaindb/nginx_https:unstable .

docker push bigchaindb/nginx_https:unstable
