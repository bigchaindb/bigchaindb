#!/bin/sh
echo "Starting MonogoDB"

pkill mongod
mongod &

sleep 3600
