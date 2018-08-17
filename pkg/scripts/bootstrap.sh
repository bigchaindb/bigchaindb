#!/usr/bin/env bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


BASEDIR="${BASH_SOURCE%/*}"
if [[ ! -d "$BASEDIR" ]]; then BASEDIR="$PWD"; fi
. "$BASEDIR/bootstrap_constants.sh"
. "$BASEDIR/bootstrap_helper.sh"

# OS ID(centos, debian, fedora, ubuntu)
OS=""
# OS Version(7, 9, 24, 16.04)
VER=""
# OP (install, uninstall)
OPERATION=${OPERATION:=""}

# Parsing arguments
while [[ $# -gt 1 ]]; do
    arg="$1"
    case $arg in
        --operation)
          OPERATION="$2"
          shift
        ;;
        *)
            echo "Unknown option: $1"
            exit 1
        ;;
    esac
    shift
done

# sanity checks
if [[ -z "${OPERATION:?Missing '--operation' [install,uninstall])}" ]] ; then
    exit 1
fi

validate_os_configuration(){
    valid_os=1
    if [ -f $1 ]; then
        . $1
        OS=$ID
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    elif [ "$(uname -s)" == "Darwin" ]; then
        echo "Using macOS"
        OS="macOS"
        VER="None"
        valid_os=True
        return
    else
        echo "Cannot find $OS_CONF. Pass arguments to your OS configurations: NAME, VERSION_ID.
        Supported OS(s) are: [ ${SUPPORTED_OS[*]} ]."
        exit 1
    fi
    for os in "${SUPPORTED_OS[@]}"; do
        if [[ $os = $OS ]]; then
            valid_os=true
            break
        fi
    done
}

validate_os_configuration $OS_CONF
echo "Operation Sytem: $OS"
echo "Version: $VER"
# Installing dependencies
if [ "$OPERATION" = "install" ]; then
  install_deps=$(validate_os_version_and_deps true $OS $VER)
  if [[ $install_deps -eq 1 ]]; then
      for dep in "${OS_DEPENDENCIES[@]}"
      do
        install_"$dep" $OS
      done
  elif [[ $install_deps -eq 2 ]]; then
      echo "Unsupported $OS Version: $VER"
  else
      echo "Dependencies already installed:[ ${OS_DEPENDENCIES[*]} ]"
  fi
# Uninstalling dependencies
elif [ "$OPERATION" = "uninstall" ]; then
  uninstall_deps=$(validate_os_version_and_deps true $OS $VER)
  if [[ $install_deps -eq 1 ]]; then
    echo "Dependencies already uninstalled:[ ${OS_DEPENDENCIES[*]} ]"
  elif [[ $install_deps -eq 2 ]]; then
      echo "Unsupported $OS Version: $VER"
  else
      for dep in "${OS_DEPENDENCIES[@]}"
      do
        uninstall_"$dep" $OS
      done
  fi
else
  echo "Invalid Operation specified. Only [install, uninstall] are supported."
  exit 1
fi
