#!/usr/bin/env bash

# ``stack.sh`` is an opinionated BigchainDB developer installation.  It
# installs and configures **BigchainDb Server**, **Tendermint Server**,
# **MongoDB**

# Print the commands being run so that we can see the command that triggers
# an error.  It is also useful for following along as the install occurs.
set -o xtrace

# Make sure umask is sane
umask 022

# Keep track of the stack.sh directory
TOP_DIR=$(cd $(dirname "$0") && pwd)
BASE_DIR=${TOP_DIR}/../..

# Check for uninitialized variables, a big cause of bugs
NOUNSET=${NOUNSET:-}
if [[ -n "$NOUNSET" ]]; then
    set -o nounset
fi

# Set default MongoDB version
if [[ "$MONGO_VERSION" = "" ]]; then
    MONGO_VERSION="3.4"
fi

# Set default tendermint version
if [[ "$TM_VERSION" = "" ]]; then
    TM_VERSION="0.12.1"
fi

# Configuration
# =============

# Source utility functions
source ${TOP_DIR}/functions-common

# Configure Distro Repositories
# -----------------------------

# For Debian/Ubuntu make apt attempt to retry network ops on it's own and mongodb pub key
# source repo
if is_ubuntu; then
    echo 'APT::Acquire::Retries "20";' | sudo tee /etc/apt/apt.conf.d/80retry  >/dev/null
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
    echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/${MONGO_VERSION} multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-${MONGO_VERSION}.list
fi

# Ensure required packages are installed
# --------------------------------------

is_package_installed python3 || install_package python3
is_package_installed python3-pip || install_package python3-pip
is_package_installed libffi-dev || install_package libffi-dev
is_package_installed libssl-dev || install_package libssl-dev
is_package_installed tmux || install_package tmux
is_package_installed mongodb-org || install_package mongodb-org
is_package_installed unzip || install_package unzip
install_tendermint_bin

# Clean system if re-running the script
OIFS=$IFS
IFS=':'
session_str=$(tmux ls | grep -w bdb-dev)
if [[ $session_str = "" ]]; then
    continue
else
    session=($session_str)
    tmux kill-session -t ${session[0]}
fi

# Stop bigchaindb service
if is_running "bigchaindb"; then
    sudo pkill bigchaindb
fi

# Stop tendermint service
if is_running "tendermint"; then
    sudo pkill tendermint
fi

# Stop mongodb service
if is_running "monogod"; then
    sudo pkill mongod
fi

sleep 5

# Create data dir for mongod
if [[ ! -d /data/db ]]; then
    sudo mkdir -p /data/db
fi
sudo chmod -R 700 /data/db

# Configure tendermint
tendermint init

# Configure tmux
cd ${BASE_DIR}
tmux new-session -s bdb-dev -n bdb -d
tmux new-window -n mdb
tmux new-window -n tendermint

# Start MongoDB
tmux send-keys -t bdb-dev:mdb 'sudo mongod --replSet=bigchain-rs' C-m

# Start BigchainDB
tmux send-keys -t bdb-dev:bdb 'sudo python3 setup.py install && bigchaindb -y configure mongodb && bigchaindb -l DEBUG start' C-m

while ! is_running "bigchaindb"; do
    echo "Waiting bigchaindb service to start"
    sleep 5
done

# Start tendermint service
tmux send-key -t bdb-dev:tendermint 'tendermint init && tendermint unsafe_reset_all && tendermint node' C-m

# Configure Error Traps
# ---------------------

# Kill background processes on exit
trap exit_trap EXIT
function exit_trap {
    exit $?
}
# Exit on any errors so that errors don't compound and kill if any services already started
trap err_trap ERR
function err_trap {
    local r=$?
    tmux kill-session bdb-dev
    set +o xtrace
    exit $?
}

# Begin trapping error exit codes
set -o errexit
