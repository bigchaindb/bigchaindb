#!/bin/bash

. ./bootstrap_constants.sh

validate_os_version_and_deps(){
    if $1; then
        case $2 in
            ubuntu)
                apt-get install bc -y > /dev/null 2>&1
                if [[ ($(echo $3 | bc) > $MINIMUM_UBUNTU_VERSION)
                    || ($(echo $3 | bc) == $MINIMUM_UBUNTU_VERSION)]]; then
                    dpkg -s "${OS_DEPENDENCIES[@]}" > /dev/null 2>&1
                    echo $?
                else
                    echo "Supported $2 Versions: >= $MINIMUM_UBUNTU_VERSION"
                    exit 1
                fi
            ;;
            centos)
                yum install bc -y > /dev/null 2>&1
                if [[ ($(echo $3 | bc) > $MINIMUM_CENTOS_VERSION)
                    || ($(echo $3 | bc) == $MINIMUM_CENTOS_VERSION) ]]; then
                    rpm -q "${OS_DEPENDENCIES[@]}" > /dev/null 2>&1
                    echo $?
                else
                    echo "Supported $2 Versions: >= $MINIMUM_CENTOS_VERSION"
                    exit 1
                fi
            ;;
            fedora)
                dnf install bc python2-dnf libselinux-python -y > /dev/null 2>&1
                if [[ ($(echo $3 | bc) > $MINIMUM_FEDORA_VERSION)
                    || ($(echo $3 | bc) == $MINIMUM_FEDORA_VERSION) ]]; then
                    rpm -q "${OS_DEPENDENCIES[@]}" > /dev/null 2>&1
                    echo $?
                else
                    echo "Supported $2 Versions: >= $MINIMUM_FEDORA_VERSION"
                    exit 1
                fi
            ;;
            *)
                echo "Supported OS(s) are: [ ${SUPPORTED_OS[*]} ]."
                exit 1
            ;;
        esac
    else
        echo "Supported OS(s) are: [ ${SUPPORTED_OS[*]} ]."
        exit 1
    fi
}

install_dependencies() {
    case $1 in
        ubuntu)
            install_deps_deb
        ;;
        centos)
            install_deps_centos
        ;;
        fedora)
            install_deps_fedora
        ;;
        *)
            echo "Supported OS(s) are: [ ${SUPPORTED_OS[*]} ]."
            exit 1
        ;;
    esac
}

#TODO: muawiakh(Currently only ansible is required. Make it generic for
# multiple dependencies)
install_deps_deb() {
    echo "Installing Dependencies..."
    apt-get update -y
    apt-get install -y software-properties-common
    apt-add-repository ppa:ansible/ansible
    apt-get update -y
    apt-get install -y "${OS_DEPENDENCIES[@]}"
}
install_deps_centos() {
    echo "Installing Dependencies..."
    yum install epel-release -y
    yum install -y https://centos7.iuscommunity.org/ius-release.rpm
    yum install "${OS_DEPENDENCIES[@]}" -y
}
install_deps_fedora() {
    echo "Installing Dependencies..."
    export LC_ALL=C
    dnf makecache
    echo "${OS_DEPENDENCIES[@]}"
    dnf -y install "${OS_DEPENDENCIES[@]}"
}
