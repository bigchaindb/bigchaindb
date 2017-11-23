#!/usr/bin/env bash


set -x
set -o xtrace

# Check for uninitialized variables, a big cause of bugs
NOUNSET=${NOUNSET:-}
if [[ -n "$NOUNSET" ]]; then
    set -o nounset
fi

# Stop if any command fails.
set -e

function usage
{
    cat << EOM

    Usage: $ bash ${0##*/} [-v] [-h] [STACK] [GIT_BRANCH]

    Installs the BigchainDB devstack or network.

    This script captures a log of all output produced during runtime, and saves
    it in a .log file within the current directory.

    STACK
        Either 'devstack' or 'network'. Network mimics a production network
        environment with multiple BDB nodes, whereas devstack is useful if 
        you plan on modifying the bigchaindb code.
        Defualts to STACK environment variable

    GIT_BRANCH
        The bigchaindb repo branch to use. defaults to GIT_BRANCH environment
        variable

    -v
        Verbose output from ansible playbooks.

    -h
        Show this help and exit.

EOM
}


ERROR='\033[0;31m' # Red
WARN='\033[1;33m' # Yellow
SUCCESS='\033[0;32m' # Green
NC='\033[0m' # No Color

# Output verbosity
verbosity=0
# BRANCH
branch=""

while getopts "vh" opt; do
    case "$opt" in
        v)
            verbosity=1
            ;;
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

shift "$((OPTIND-1))" # Shift off the options we've already parsed

# STACK is a required positional argument.
if [[ $1 ]]; then
    stack=$1
else
    stack=$STACK
fi
shift

# RELEASE is an optional positional argument, defaulting to BRANCH.
if [[ $1 ]]; then
    git_branch=$1
else
    git_branch=$GIT_BRANCH
fi


if [[ ! $git_branch ]]; then
    echo "You must specify BRANCH, or set BDB_BRANCH before running."
    exit 1
fi

# If there are positional arguments left, something is wrong.
if [[ $1 ]]; then
    echo "Don't understand extra arguments: $*"
    usage
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

export BRANCH=$release
echo "Using bigchaindb branch '$BRANCH'"

if [[ -d .vagrant ]]; then
    echo -e "${ERROR}A .vagrant directory already exists here. If you already tried installing $stack, make sure to vagrant destroy the $stack machine and 'rm -rf .vagrant' before trying to reinstall. If you would like to install a separate $stack, change to a different directory and try running the script again.${NC}"
    exit 1
fi

git clone https://github.com/bigchaindb/bigchaindb.git -b $BRANCH

if [[ $stack == "devstack" ]]; then # Install devstack
    curl -fOL# https://raw.githubusercontent.com/bigchaindb/bigchaindb/${BRANCH}/pkg/scripts/Vagrantfile
    vagrant up --provider virtualbox
elif [[ $stack == "network" ]]; then # Install network
    echo -e "${WARN}Network support is not yet available"
    exit
else # Throw error
    echo -e "${ERROR}Unrecognized stack name, must be either devstack or network${NC}"
    exit 1
fi

echo -e "${SUCCESS}Finished installing! You may now log in using 'vagrant ssh'"
