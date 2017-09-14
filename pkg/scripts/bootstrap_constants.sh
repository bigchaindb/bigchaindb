#!/bin/bash
OS_CONF=/etc/os-release
declare -a SUPPORTED_OS=('ubuntu' 'centos' 'fedora')
declare -a OS_DEPENDENCIES=('ansible')
MINIMUM_UBUNTU_VERSION=16.04
MINIUMUM_CENTOS_VERSION=7
MINIMIUM_FEDORA_VERSION=24