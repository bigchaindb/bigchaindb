#!/bin/bash
set -euo pipefail

BASE_DIR=$(pwd)
APICAST_RELEASE="3.1.0"
BASE_GIT_URL="https://github.com/3scale/apicast/archive"

# Set Default config
export APICAST_CONFIGURATION_LOADER="boot" # Overriding apicast default lazy config loader
export APICAST_MANAGEMENT_API="debug" # Overriding apicast default fo 'status' mode to be
                                      # able to update bigchaindb backen service endpoint

# Sanity Check
if [[ -z "${THREESCALE_PORTAL_ENDPOINT:?THREESCALE_PORTAL_ENDPOINT not specified. Exiting!}" || \
      -z "${BIGCHAINDB_BACKEND_HOST:?BIGCHAINDB_BACKEND_HOST not specified. Exiting!}" || \
      -z "${BIGCHAINDB_API_PORT:?BIGCHAINDB_API_PORT not specified. Exiting!}" ]]; then
  exit 1
fi

export THREESCALE_PORTAL_ENDPOINT=`printenv THREESCALE_PORTAL_ENDPOINT`

# Print Current Configs
echo "Apicast Release: ${APICAST_RELEASE}"
echo "Apicast Download URL: ${BASE_GIT_URL}"
echo "APICAST_CONFIGURATION_LOADER: ${APICAST_CONFIGURATION_LOADER}"
echo "BIGCHAINDB_BACKEND_HOST: ${BIGCHAINDB_BACKEND_HOST}"
echo "BIGCHAINDB_API_PORT: ${BIGCHAINDB_API_PORT}"

# Download and Install Apicast
wget "${BASE_GIT_URL}/v${APICAST_RELEASE}.tar.gz"
tar -xvzf "v${APICAST_RELEASE}.tar.gz"

eval luarocks make apicast-${APICAST_RELEASE}/apicast/*.rockspec --tree /usr/local/openresty/luajit

# Start nginx
echo "INFO: starting nginx..."
exec apicast-${APICAST_RELEASE}/apicast/bin/apicast -b -e production -v -v -v