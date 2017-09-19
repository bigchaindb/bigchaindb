#!/bin/bash
set -e

. ./bootstrap_constants.sh
. ./bootstrap_helper.sh

# OS ID(ubuntu, centos, fedora)
OS=""
# OS Version(16.04, 7, 24)
VER=""

# Parsing arguments
while [[ $# -gt 1 ]]; do
    arg="$1"
    case $arg in
        --os)
            OS="$2"
            shift
        ;;
        --os-version)
            VER="$2"
            shift
        ;;
        *)
            echo "Unknown option: $1"
            exit 1
        ;;
    esac
    shift
done

validate_os_configuration(){
    valid_os=1
    if [ -f $1 ]; then
        . $1
        OS=$ID
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    else
        echo "Cannot find $OS_CONF. Pass arguments to your OS configurations: NAME, VERSION_ID.
        Supported OS(s) are: [ ${SUPPORTED_OS[*]} ]."
        exit 1
    fi
    for os in "${SUPPORTED_OS[@]}"; do
        if [[ $os = $2 ]]; then
            valid_os=true
            break
        fi
    done
}

validate_os_configuration $OS_CONF $OS $VER
echo "Operation Sytem: $OS"
echo "Version: $VER"
install_deps=$(validate_os_version_and_deps true $OS $VER)
if [[ $install_deps -eq 1 ]]; then
    install_dependencies $OS
else
    echo "Dependencies already installed:[ ${OS_DEPENDENCIES[*]} ]"
fi