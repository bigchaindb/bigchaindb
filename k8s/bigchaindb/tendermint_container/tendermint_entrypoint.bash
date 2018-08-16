#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

set -euo pipefail

# Cluster vars
tm_persistent_peers=`printenv TM_PERSISTENT_PEERS`
tm_validators=`printenv TM_VALIDATORS`
tm_validator_power=`printenv TM_VALIDATOR_POWER`
tm_pub_key_access_port=`printenv TM_PUB_KEY_ACCESS_PORT`
tm_genesis_time=`printenv TM_GENESIS_TIME`
tm_chain_id=`printenv TM_CHAIN_ID`
tm_p2p_port=`printenv TM_P2P_PORT`


# tendermint node vars
tmhome=`printenv TMHOME`
tm_proxy_app=`printenv TM_PROXY_APP`
tm_abci_port=`printenv TM_ABCI_PORT`
tm_instance_name=`printenv TM_INSTANCE_NAME`

# Container vars
RETRIES=0
CANNOT_INITIATLIZE_INSTANCE='Cannot start instance, if initial validator(s) are unreachable.'


# sanity check
if [[ -z "${tm_persistent_peers:?TM_PERSISTENT_PEERS not specified. Exiting!}" || \
      -z "${tm_validators:?TM_VALIDATORS not specified. Exiting!}" || \
      -z "${tm_validator_power:?TM_VALIDATOR_POWER not specified. Exiting!}" || \
      -z "${tm_pub_key_access_port:?TM_PUB_KEY_ACCESS_PORT not specified. Exiting!}" || \
      -z "${tm_genesis_time:?TM_GENESIS_TIME not specified. Exiting!}" || \
      -z "${tm_chain_id:?TM_CHAIN_ID not specified. Exiting!}" || \
      -z "${tmhome:?TMHOME not specified. Exiting!}" || \
      -z "${tm_p2p_port:?TM_P2P_PORT not specified. Exiting!}" || \
      -z "${tm_abci_port:?TM_ABCI_PORT not specified. Exiting! }" || \
      -z "${tm_instance_name:?TM_INSTANCE_NAME not specified. Exiting! }" ]]; then
  echo "Missing required enviroment variables."
  exit 1
else
  echo tm_persistent_peers="$TM_PERSISTENT_PEERS"
  echo tm_validators="$TM_VALIDATORS"
  echo tm_validator_power="$TM_VALIDATOR_POWER"
  echo tm_pub_key_access_port="$TM_PUB_KEY_ACCESS_PORT"
  echo tm_genesis_time="$TM_GENESIS_TIME"
  echo tm_chain_id="$TM_CHAIN_ID"
  echo tmhome="$TMHOME"
  echo tm_p2p_port="$TM_P2P_PORT"
  echo tm_abci_port="$TM_ABCI_PORT"
  echo tm_instance_name="$TM_INSTANCE_NAME"
fi

# copy template
mkdir -p /tendermint/config
cp /etc/tendermint/genesis.json /tendermint/config/genesis.json

TM_GENESIS_FILE=/tendermint/config/genesis.json
TM_PUB_KEY_DIR=/tendermint_node_data

# configure the nginx.conf file with env variables
sed -i "s|TM_GENESIS_TIME|\"${tm_genesis_time}\"|g" ${TM_GENESIS_FILE}
sed -i "s|TM_CHAIN_ID|\"${tm_chain_id}\"|g" ${TM_GENESIS_FILE}

if [ ! -f /tendermint/config/priv_validator.json ]; then
  tendermint gen_validator > /tendermint/config/priv_validator.json
  # pub_key.json will be served by the nginx container
  cat /tendermint/config/priv_validator.json
  cat /tendermint/config/priv_validator.json | jq ".pub_key" > "$TM_PUB_KEY_DIR"/pub_key.json
fi

if [ ! -f /tendermint/config/node_key.json ]; then
  tendermint gen_node_key > "$TM_PUB_KEY_DIR"/address
fi

# fill genesis file with validators
IFS=',' read -ra VALS_ARR <<< "$TM_VALIDATORS"
IFS=',' read -ra VAL_POWERS_ARR <<< "$TM_VALIDATOR_POWER"
if [ ${#VALS_ARR[@]} -ne ${#VAL_POWERS_ARR[@]} ]; then
  echo "Invalid configuration of Validator(s) and Validator Power(s)"
  exit 1
fi
for i in "${!VALS_ARR[@]}"; do
  # wait until validator generates priv/pub key pair
  set +e
  echo Validator: "${VALS_ARR[$i]}"
  echo Validator Power: "${VAL_POWERS_ARR[$i]}"
  echo "http://${VALS_ARR[$i]}:$tm_pub_key_access_port/pub_key.json"
  curl -s --fail "http://${VALS_ARR[$i]}:$tm_pub_key_access_port/pub_key.json" > /dev/null
  ERR=$?
  while [ "$ERR" != 0 ]; do
    RETRIES=$((RETRIES+1))
    if [ $RETRIES -eq 10 ]; then
      echo "${CANNOT_INITIATLIZE_INSTANCE}"
      exit 1
    fi
    # 300(30 * 10(retries)) second timeout before container dies if it cannot find initial peers
    sleep 30
    curl -s --fail "http://${VALS_ARR[$i]}:$tm_pub_key_access_port/pub_key.json" > /dev/null
    ERR=$?
    echo "Cannot get public key for Tendermint instance: ${VALS_ARR[$i]}"
  done
  set -e
  # add validator to genesis file along with its pub_key
  curl -s "http://${VALS_ARR[$i]}:$tm_pub_key_access_port/pub_key.json" | jq ". as \$k | {pub_key: \$k, power: \"${VAL_POWERS_ARR[$i]}\", name: \"${VALS_ARR[$i]}\"}" > pub_validator.json
  cat /tendermint/config/genesis.json | jq ".validators |= .+ [$(cat pub_validator.json)]" > tmpgenesis && mv tmpgenesis /tendermint/config/genesis.json
  rm pub_validator.json
done

# construct persistent peers
IFS=',' read -ra PEERS_ARR <<< "$tm_persistent_peers"
peers=()
for s in "${PEERS_ARR[@]}"; do
  echo "http://$s:$tm_pub_key_access_port/address"
  curl -s --fail "http://$s:$tm_pub_key_access_port/address" > /dev/null
  ERR=$?
  while [ "$ERR" != 0 ]; do
    RETRIES=$((RETRIES+1))
    if [ $RETRIES -eq 10 ]; then
      echo "${CANNOT_INITIATLIZE_INSTANCE}"
      exit 1
    fi
    # 300(30 * 10(retries)) second timeout before container dies if it cannot find initial peers
    sleep 30
    curl -s --fail "http://$s:$tm_pub_key_access_port/address" > /dev/null
    ERR=$?
    echo "Cannot get address for Tendermint instance: ${s}"
  done
  peer_addr=$(curl -s "http://$s:$tm_pub_key_access_port/address")
  peers+=("$peer_addr@$s:$tm_p2p_port")
done
peers=$(IFS=','; echo "${peers[*]}")

# start nginx
echo "INFO: starting tendermint..."
exec tendermint node --p2p.persistent_peers="$peers" --moniker="$tm_instance_name" --proxy_app="tcp://$tm_proxy_app:$tm_abci_port" --consensus.create_empty_blocks=false --p2p.pex=false
