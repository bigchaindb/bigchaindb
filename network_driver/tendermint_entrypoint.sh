#!/bin/sh
echo "Starting Tendermint"

pkill tendermint
/go/bin/tendermint node &

sleep 3600
