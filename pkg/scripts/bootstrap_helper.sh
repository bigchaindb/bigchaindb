#!/usr/bin/env bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


BASEDIR="${BASH_SOURCE%/*}"
if [[ ! -d "$BASEDIR" ]]; then BASEDIR="$PWD"; fi
. "$BASEDIR/bootstrap_constants.sh"

validate_os_version_and_deps(){
    if $1; then
        case $2 in
            centos)
                if [[ ($(version_compare_gt $3 $MINIMUM_CENTOS_VERSION) == 0)
                    || ($(version_compare_eq $3 $MINIMUM_CENTOS_VERSION) == 0) ]]; then
                    rpm -q "${OS_DEPENDENCIES[@]}" > /dev/null 2>&1
                    echo $?
                else
                    echo 2
                fi
            ;;
            debian)
                if [[ ($(version_compare_gt $3 $MINIMUM_DEBIAN_VERSION) == 0)
                    || ($(version_compare_eq $3 $MINIMUM_DEBIAN_VERSION) == 0) ]]; then
                    dpkg -s "${OS_DEPENDENCIES[@]}" > /dev/null 2>&1
                    echo $?
                else
                    echo 2
                fi
            ;;
            fedora)
                if [[ ($(version_compare_gt $3 $MINIMUM_FEDORA_VERSION) == 0)
                    || ($(version_compare_eq $3 $MINIMUM_FEDORA_VERSION) == 0) ]]; then
                    rpm -q "${OS_DEPENDENCIES[@]}" > /dev/null 2>&1
                    echo $?
                else
                    echo 2
                fi
            ;;
            ubuntu)
                if [[ ($(version_compare_gt $3 $MINIMUM_UBUNTU_VERSION) == 0)
                    || ($(version_compare_eq $3 $MINIMUM_UBUNTU_VERSION) == 0) ]]; then
                    dpkg -s "${OS_DEPENDENCIES[@]}" > /dev/null 2>&1
                    echo $?
                else
                    echo 2
                fi
            ;;
            macOS)
                pip show "${OS_DEPENDENCIES[@]}" > /dev/null 2>&1
                echo $?
            ;;
            *)
                echo "Supported OS(s) are: [ ${SUPPORTED_OS[*]} ]."
                exit 1
            ;;
        esac
    else
        echo "Supported OS(s) are: [ ${SUPPORTED_OS[*]} ]."
    fi
}

version_compare_gt(){
  test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"
  echo $?
}

version_compare_eq(){
  test "$(printf '%s\n' "$@" | sort -V | head -n 1)" == "$2"
  echo $?
}


install_ansible() {
    echo "Installing Ansible..."
    case $1 in
      centos)
        yum install epel-release -y
        yum install -y https://centos7.iuscommunity.org/ius-release.rpm
        yum install ansible -y
      ;;
      debian)
          apt-get update -y && apt-get install --fix-missing
          apt-get install lsb-release software-properties-common gnupg -y
          echo "deb http://ppa.launchpad.net/ansible/ansible/ubuntu trusty main" | tee -a /etc/apt/sources.list.d/ansible-debian.list
          apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367
          apt-get update
          apt-get install -y ansible
          echo 'localhost' > /etc/ansible/hosts
      ;;
      fedora)
        export LC_ALL=C
        dnf makecache
        dnf -y install ansible
      ;;
      macOS)
        easy_install pip
        pip install ansible
      ;;
      ubuntu)
        apt-get update -y
        apt-get install -y software-properties-common
        apt-add-repository ppa:ansible/ansible -y
        apt-get update -y
        apt-get install -y ansible
      ;;
      *)
        echo "Supported OS(s) are: [ ${SUPPORTED_OS[*]} ]."
    esac
}

uninstall_ansible() {
    echo "Uninstalling Ansible..."
    case $1 in
      centos)
        yum remove ansible -y
      ;;
      debian)
        apt-get purge ansible -y
      ;;
      fedora)
        export LC_ALL=C
        dnf remove ansible -y
      ;;
      macOS)
        pip uninstall ansible -y
      ;;
      ubuntu)
        apt-get purge ansible -y
      ;;
      *)
        echo "Supported OS(s) are: [ ${SUPPORTED_OS[*]} ]."
    esac
}
