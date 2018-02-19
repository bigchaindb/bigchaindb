#!/bin/bash
set -euo pipefail

BASE_DIR=$(pwd)
APICAST_RELEASE="3.1.0"
BASE_GIT_URL="https://github.com/3scale/apicast/archive"


# Sanity Check
if [[ -z "${THREESCALE_PORTAL_ENDPOINT:?THREESCALE_PORTAL_ENDPOINT not specified. Exiting!}" || \
      -z "${BDB_SERVICE_ENDPOINT:?bigchaindb backend service endpoint not specified. Exiting!}" ]]; then
  exit 1
fi

# Download and Install Apicast
wget "${BASE_GIT_URL}/v${APICAST_RELEASE}.tar.gz"
tar -xvzf "v${APICAST_RELEASE}.tar.gz"

luarocks make apicast-${APICAST_RELEASE}/apicast/*.rockspec --tree /usr/local/openresty/luajit



# Set Default config
export APICAST_CONFIGURATION_LOADER="boot" # Overriding apicast default lazy config loader
export APICAST_MANAGEMENT_API="debug" # Overriding apicast default fo 'status' mode to be
                                      # able to update service endpoint from https://test.bigchaindb.com
                                      # to local service endpoint

# Print Current Configs
echo "Apicast Release: ${APICAST_RELEASE}"
echo "Apicast Download URL: ${BASE_GIT_URL}"
echo "APICAST_CONFIGURATION_LOADER: ${APICAST_CONFIGURATION_LOADER}"
echo "BDB_SERVICE_ENDPOINT: ${BDB_SERVICE_ENDPOINT}"


# Start nginx
echo "INFO: starting nginx..."
exec apicast-${APICAST_RELEASE}/apicast/bin/apicast -b -e production -v -v -v
