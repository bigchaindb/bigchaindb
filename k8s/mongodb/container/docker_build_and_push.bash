#!/bin/bash

docker build -t bigchaindb/mongodb:3.0 .

docker push bigchaindb/mongodb:3.0
