#!/bin/bash

docker build -t bigchaindb/nginx_pub_key_access:2.0.0-alpha3 .

docker push bigchaindb/nginx_pub_key_access:2.0.0-alpha3
