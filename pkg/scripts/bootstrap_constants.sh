#!/usr/bin/env bash
OS_CONF=/etc/os-release
declare -a SUPPORTED_OS=('centos' 'fedora' 'ubuntu' 'debian' 'macOS')
declare -a OS_DEPENDENCIES=('ansible')
MINIMUM_UBUNTU_VERSION=16.04
MINIUMUM_CENTOS_VERSION=7
MINIMIUM_FEDORA_VERSION=24
MINIMUM_DEBIAN_VERSION=8