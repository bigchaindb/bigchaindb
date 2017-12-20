#!/usr/bin/env bash

set -o nounset
set -o errexit

function usage
{
    cat << EOM

    Usage: $ bash ${0##*/} [-v] [-h]

    Installs the BigchainDB devstack or network.

    ENV[STACK]
        Set STACK environment variable to Either 'devstack' or 'network'.
        Network mimics a production network environment with multiple BDB
        nodes, whereas devstack is useful if you plan on modifying the
        bigchaindb code.

    ENV[GIT_BRANCH]
        To configure bigchaindb repo branch to use set GIT_BRANCH environment
        variable

    ENV[TM_VERSION]
        Tendermint version to use for the devstack setup

    ENV[MONGO_VERSION]
        MongoDB version to use with the devstack setup

    -v
        Verbose output from ansible playbooks.

    -h
        Show this help and exit.

EOM
}

# GIT_BRANCH
git_branch=$GIT_BRANCH

while getopts "h" opt; do
    case "$opt" in
        h)
            usage
            exit
            ;;
        *)
            usage
            exit 1
            ;;
    esac
done

if [[ ! $git_branch ]]; then
    echo "You must specify GIT_BRANCH before running."
    echo
    echo usage
    exit 1
fi

mkdir -p logs
log_file=logs/install-$(date +%Y%m%d-%H%M%S).log
exec > >(tee $log_file) 2>&1
echo "Capturing output to $log_file"
echo "Installation started at $(date '+%Y-%m-%d %H:%M:%S')"

function finish {
    echo "Installation finished at $(date '+%Y-%m-%d %H:%M:%S')"
}
trap finish EXIT

export GIT_BRANCH=$git_branch
echo "Using bigchaindb branch '$GIT_BRANCH'"

git clone https://github.com/bigchaindb/bigchaindb.git -b $GIT_BRANCH || true
curl -fOL# https://raw.githubusercontent.com/bigchaindb/bigchaindb/${GIT_BRANCH}/pkg/scripts/Vagrantfile
vagrant up --provider virtualbox

echo -e "Finished installing! You may now log in using 'vagrant ssh'"
echo -e "Once inside the VM do 'tmux attach' to attach to tmux session running all services"
