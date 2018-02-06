#!/bin/bash

docker build -t bigchaindb/mongodb:3.4 .

docker push bigchaindb/mongodb:3.4
