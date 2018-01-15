#!/bin/sh
echo "Starting Tendermint"

/go/bin/tendermint node --proxy_app=dummy &

sleep 3600
