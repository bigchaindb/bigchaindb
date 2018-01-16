#!/bin/sh
echo "Starting Tendermint"

if [ "$1" != "" ] && [ "$2" != "" ] ; then
    echo $1 > /tendermint/priv_validator.json
    echo $2 > /tendermint/genesis.json
fi

pkill tendermint
/go/bin/tendermint node &

sleep 3600
