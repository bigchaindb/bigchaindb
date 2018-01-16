#!/bin/sh
echo "Starting BigchainDB"

pkill bigchaindb
bigchaindb start &

sleep 3600
