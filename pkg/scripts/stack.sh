#!/usr/bin/env bash

# ``stack.sh`` is an opinionated BigchainDB developer installation.  It
# installs and configures **BigchainDb Server**, **Tendermint Server**,
# **MongoDB**

# To keep this script simple we assume you are running on a recent **Ubuntu**
# (16.04 Xenial or newer)

# Print the commands being run so that we can see the command that triggers
# an error.  It is also useful for following along as the install occurs.
set -o xtrace

# Make sure umask is sane
umask 022

# Initialize variables:
LAST_SPINNER_PID=""
STACK_USER="stack"

# Keep track of the stack.sh directory
TOP_DIR=$(cd $(dirname "$0") && pwd)

# Check for uninitialized variables, a big cause of bugs
NOUNSET=${NOUNSET:-}
if [[ -n "$NOUNSET" ]]; then
    set -o nounset
fi

# Set start of devstack timestamp
DEVSTACK_START_TIME=$(date +%s)

# Configuration
# =============


# Prepare the environment
# -----------------------

source functions-common

# Initialize variables:
LAST_SPINNER_PID=""

# Determine what system we are running on.  This provides ``os_VENDOR``,
# ``os_RELEASE``, ``os_PACKAGE``, ``os_CODENAME``
# and ``DISTRO``
GetDistro

# Configure Distro Repositories
# -----------------------------

# For Debian/Ubuntu make apt attempt to retry network ops on it's own
if is_ubuntu; then
    echo 'APT::Acquire::Retries "20";' | sudo tee /etc/apt/apt.conf.d/80retry  >/dev/null
fi

# Ensure required packages are installed
# --------------------------------------
is_package_installed python3 || install_package python3
is_package_installed python3-pip || install_package python3-pip
is_package_installed libffi-dev || install_package libffi-dev
is_package_installed libssl-dev || install_package libssl-dev

# Configure Logging
# -----------------

# Set up logging level
VERBOSE=$(trueorfalse True VERBOSE)

# Draw a spinner so the user knows something is happening
function spinner {
    local delay=0.75
    local spinstr='/-\|'
    printf "..." >&3
    while [ true ]; do
        local temp=${spinstr#?}
        printf "[%c]" "$spinstr" >&3
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b" >&3
    done
}

function kill_spinner {
    if [ ! -z "$LAST_SPINNER_PID" ]; then
        kill >/dev/null 2>&1 $LAST_SPINNER_PID
        printf "\b\b\bdone\n" >&3
    fi
}

# Echo text to the log file, summary log file and stdout
# echo_summary "something to say"
function echo_summary {
    if [[ -t 3 && "$VERBOSE" != "True" ]]; then
        kill_spinner
        echo -n -e $@ >&6
        spinner &
        LAST_SPINNER_PID=$!
    else
        echo -e $@ >&6
    fi
}

# Configure Error Traps
# ---------------------

# Kill background processes on exit
trap exit_trap EXIT
function exit_trap {
    # Kill the last spinner process
    kill_spinner
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
