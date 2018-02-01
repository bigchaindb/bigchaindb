#!/bin/bash

docker build -t bigchaindb/nginx_https:unstable-tmt .

docker push bigchaindb/nginx_https:unstable-tmt
