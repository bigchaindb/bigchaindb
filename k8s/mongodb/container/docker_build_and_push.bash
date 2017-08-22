#!/bin/bash

docker build -t bigchaindb/mongodb:3.1 .

docker push bigchaindb/mongodb:3.1
