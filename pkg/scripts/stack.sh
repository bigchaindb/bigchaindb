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

# Check for uninitialized variables, a big cause of bugs
NOUNSET=${NOUNSET:-}
if [[ -n "$NOUNSET" ]]; then
    set -o nounset
fi

# Configuration
# =============

# Source utility functions
source ${TOP_DIR}/functions-common

# Determine what system we are running on.  This provides ``os_VENDOR``,
# ``os_RELEASE``, ``os_PACKAGE``, ``os_CODENAME``
# and ``DISTRO``
GetDistro

# Configure Distro Repositories
# -----------------------------

# For Debian/Ubuntu make apt attempt to retry network ops on it's own and mongodb pub key
# source repo
if is_ubuntu; then
    echo 'APT::Acquire::Retries "20";' | sudo tee /etc/apt/apt.conf.d/80retry  >/dev/null
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
    echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
fi

# Ensure required packages are installed
# --------------------------------------

is_package_installed python3 || install_package python3
is_package_installed python3-pip || install_package python3-pip
is_package_installed libffi-dev || install_package libffi-dev
is_package_installed libssl-dev || install_package libssl-dev
is_package_installed tmux || install_package tmux
is_package_installed mongodb-org || install_package mongodb-org


# Configure Error Traps
# ---------------------

# Kill background processes on exit
trap exit_trap EXIT
function exit_trap {
    exit $?
}

# Exit on any errors so that errors don't compound
trap err_trap ERR
function err_trap {
    local r=$?
    set +o xtrace
    exit $?
}

# Begin trapping error exit codes
set -o errexit
