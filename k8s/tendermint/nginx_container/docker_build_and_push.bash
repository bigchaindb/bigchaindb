#!/bin/bash

docker build -t bigchaindb/nginx_pub_key_access:unstable-tmt .

docker push bigchaindb/nginx_pub_key_access:unstable-tmt
