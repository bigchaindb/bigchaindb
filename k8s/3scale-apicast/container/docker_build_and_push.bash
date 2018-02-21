#!/bin/bash

docker build -t bigchaindb/nginx_3scale:unstable .

docker push bigchaindb/nginx_3scale:unstable
