#!/bin/bash

docker build -t bigchaindb/nginx_pub_key_access:2.0.0-alpha .

docker push bigchaindb/nginx_pub_key_access:2.0.0-alpha
