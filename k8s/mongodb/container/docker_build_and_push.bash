#!/bin/bash

docker build -t bigchaindb/mongodb:3.2 .

docker push bigchaindb/mongodb:3.2
