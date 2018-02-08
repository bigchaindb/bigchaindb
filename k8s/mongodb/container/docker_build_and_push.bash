#!/bin/bash

docker build -t bigchaindb/mongodb:3.3 .

docker push bigchaindb/mongodb:3.3
