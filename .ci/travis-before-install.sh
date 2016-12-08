#!/bin/bash

apt-get update -qq
wget https://github.com/miloyip/rapidjson/archive/v1.1.0.tar.gz -O /tmp/v1.1.0.tar.gz
tar -xvf /tmp/v1.1.0.tar.gz
cp -r $PWD/rapidjson-1.1.0/include/rapidjson /usr/include/
