#!/usr/bin/env bash

# ``stack.sh`` is an opinionated BigchainDB developer installation.  It
# installs and configures **BigchainDb Server**, **Tendermint Server**,
# **MongoDB**

# To keep this script simple we assume you are running on a recent **Ubuntu**
# (16.04 Xenial or newer)

# Print the commands being run so that we can see the command that triggers
# an error.  It is also useful for following along as the install occurs.
set -o xtrace

# Make sure umask is sane
umask 022

# Initialize variables:
LAST_SPINNER_PID=""
STACK_USER="stack"

# Keep track of the stack.sh directory
TOP_DIR=$(cd $(dirname "$0") && pwd)

# Check for uninitialized variables, a big cause of bugs
NOUNSET=${NOUNSET:-}
if [[ -n "$NOUNSET" ]]; then
    set -o nounset
fi

# Set start of devstack timestamp
DEVSTACK_START_TIME=$(date +%s)

# Configuration
# =============

# Sanity Checks
# -------------

# Clean up last environment var cache
if [[ -r $TOP_DIR/.stackenv ]]; then
    rm $TOP_DIR/.stackenv
fi

# stack.sh is designed to be run as a non-root user;
# ``stack.sh`` must not be run as **root**.  It aborts and suggests one course of
# action to create a suitable user account.
if [[ $EUID -eq 0 ]]; then
    set +o xtrace
    echo "stack.sh should be run as a user with sudo permissions, "
    echo "not root."
    exit 1
fi

OS=$(uname -s)

if [[ ! ${OS} =~ "Linux" ]]; then
    set +o xtrace
    echo "stack.sh is currently only supported on Linux Systems"
    exit 1
fi

# Prepare the environment
# -----------------------

source functions-common

# Initialize variables:
LAST_SPINNER_PID=""

# Determine what system we are running on.  This provides ``os_VENDOR``,
# ``os_RELEASE``, ``os_PACKAGE``, ``os_CODENAME``
# and ``DISTRO``
GetDistro

# Tell users who aren't on an explicitly supported distro
if [[ ! ${DISTRO} =~ (xenial) ]]; then
    echo "ERROR: this script is not supported on $DISTRO"
    die $LINENO
fi


# Configure Distro Repositories
# -----------------------------

# For Debian/Ubuntu make apt attempt to retry network ops on it's own
if is_ubuntu; then
    echo 'APT::Acquire::Retries "20";' | sudo tee /etc/apt/apt.conf.d/80retry  >/dev/null
fi

# Ensure required packages are installed
# --------------------------------------
is_package_installed python3 || install_package python3
is_package_installed python3-pip || install_package python3-pip
is_package_installed libffi-dev || install_package libffi-dev
is_package_installed libssl-dev || install_package libssl-dev

exit



# Configure Logging
# -----------------

# Set up logging level
VERBOSE=$(trueorfalse True VERBOSE)

# Draw a spinner so the user knows something is happening
function spinner {
    local delay=0.75
    local spinstr='/-\|'
    printf "..." >&3
    while [ true ]; do
        local temp=${spinstr#?}
        printf "[%c]" "$spinstr" >&3
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b" >&3
    done
}

function kill_spinner {
    if [ ! -z "$LAST_SPINNER_PID" ]; then
        kill >/dev/null 2>&1 $LAST_SPINNER_PID
        printf "\b\b\bdone\n" >&3
    fi
}

# Echo text to the log file, summary log file and stdout
# echo_summary "something to say"
function echo_summary {
    if [[ -t 3 && "$VERBOSE" != "True" ]]; then
        kill_spinner
        echo -n -e $@ >&6
        spinner &
        LAST_SPINNER_PID=$!
    else
        echo -e $@ >&6
    fi
}

# Echo text only to stdout, no log files
# echo_nolog "something not for the logs"
function echo_nolog {
    echo $@ >&3
}

# Set up logging for ``stack.sh``
# Set ``LOGFILE`` to turn on logging
# Append '.xxxxxxxx' to the given name to maintain history
# where 'xxxxxxxx' is a representation of the date the file was created
TIMESTAMP_FORMAT=${TIMESTAMP_FORMAT:-"%F-%H%M%S"}
LOGDAYS=${LOGDAYS:-7}
CURRENT_LOG_TIME=$(date "+$TIMESTAMP_FORMAT")

if [[ -n "$LOGFILE" ]]; then
    # Clean up old log files.  Append '.*' to the user-specified
    # ``LOGFILE`` to match the date in the search template.
    LOGFILE_DIR="${LOGFILE%/*}"           # dirname
    LOGFILE_NAME="${LOGFILE##*/}"         # basename
    mkdir -p $LOGFILE_DIR
    find $LOGFILE_DIR -maxdepth 1 -name $LOGFILE_NAME.\* -mtime +$LOGDAYS -exec rm {} \;
    LOGFILE=$LOGFILE.${CURRENT_LOG_TIME}
    SUMFILE=$LOGFILE.summary.${CURRENT_LOG_TIME}

    # Redirect output according to config

    # Set fd 3 to a copy of stdout. So we can set fd 1 without losing
    # stdout later.
    exec 3>&1
    if [[ "$VERBOSE" == "True" ]]; then
        # Set fd 1 and 2 to write the log file
        exec 1> >( $TOP_DIR/tools/outfilter.py -v -o "${LOGFILE}" ) 2>&1
        # Set fd 6 to summary log file
        exec 6> >( $TOP_DIR/tools/outfilter.py -o "${SUMFILE}" )
    else
        # Set fd 1 and 2 to primary logfile
        exec 1> >( $TOP_DIR/tools/outfilter.py -o "${LOGFILE}" ) 2>&1
        # Set fd 6 to summary logfile and stdout
        exec 6> >( $TOP_DIR/tools/outfilter.py -v -o "${SUMFILE}" >&3 )
    fi

    echo_summary "stack.sh log $LOGFILE"
    # Specified logfile name always links to the most recent log
    ln -sf $LOGFILE $LOGFILE_DIR/$LOGFILE_NAME
    ln -sf $SUMFILE $LOGFILE_DIR/$LOGFILE_NAME.summary
else
    # Set up output redirection without log files
    # Set fd 3 to a copy of stdout. So we can set fd 1 without losing
    # stdout later.
    exec 3>&1
    if [[ "$VERBOSE" != "True" ]]; then
        # Throw away stdout and stderr
        exec 1>/dev/null 2>&1
    fi
    # Always send summary fd to original stdout
    exec 6> >( $TOP_DIR/tools/outfilter.py -v >&3 )
fi

# Basic test for ``$DEST`` path permissions (fatal on error unless skipped)
check_path_perm_sanity ${DEST}

# Configure Error Traps
# ---------------------

# Kill background processes on exit
trap exit_trap EXIT
function exit_trap {
    local r=$?
    jobs=$(jobs -p)
    # Only do the kill when we're logging through a process substitution,
    # which currently is only to verbose logfile
    if [[ -n $jobs && -n "$LOGFILE" && "$VERBOSE" == "True" ]]; then
        echo "exit_trap: cleaning up child processes"
        kill 2>&1 $jobs
    fi

    #Remove timing data file
    if [ -f "$OSCWRAP_TIMER_FILE" ] ; then
        rm "$OSCWRAP_TIMER_FILE"
    fi

    # Kill the last spinner process
    kill_spinner

    if [[ $r -ne 0 ]]; then
        echo "Error on exit"
        # If we error before we've installed os-testr, this will fail.
        if type -p generate-subunit > /dev/null; then
            generate-subunit $DEVSTACK_START_TIME $SECONDS 'fail' >> ${SUBUNIT_OUTPUT}
        fi
        if [[ -z $LOGDIR ]]; then
            $TOP_DIR/tools/worlddump.py
        else
            $TOP_DIR/tools/worlddump.py -d $LOGDIR
        fi
    else
        # If we error before we've installed os-testr, this will fail.
        if type -p generate-subunit > /dev/null; then
            generate-subunit $DEVSTACK_START_TIME $SECONDS >> ${SUBUNIT_OUTPUT}
        fi
    fi

    exit $r
}

# Exit on any errors so that errors don't compound
trap err_trap ERR
function err_trap {
    local r=$?
    set +o xtrace
    if [[ -n "$LOGFILE" ]]; then
        echo "${0##*/} failed: full log in $LOGFILE"
    else
        echo "${0##*/} failed"
    fi
    exit $r
}

# Begin trapping error exit codes
set -o errexit

# Print the kernel version
uname -a

# Save configuration values
save_stackenv $LINENO


# Install Packages
# ================

git_clone $REQUIREMENTS_REPO $REQUIREMENTS_DIR $REQUIREMENTS_BRANCH

# Install package requirements
# Source it so the entire environment is available
echo_summary "Installing package prerequisites"
source $TOP_DIR/tools/install_prereqs.sh

# Configure an appropriate Python environment
if [[ "$OFFLINE" != "True" ]]; then
    PYPI_ALTERNATIVE_URL=${PYPI_ALTERNATIVE_URL:-""} $TOP_DIR/tools/install_pip.sh
fi

# Install subunit for the subunit output stream
pip_install -U os-testr

TRACK_DEPENDS=${TRACK_DEPENDS:-False}

# Install Python packages into a virtualenv so that we can track them
if [[ $TRACK_DEPENDS = True ]]; then
    echo_summary "Installing Python packages into a virtualenv $DEST/.venv"
    pip_install -U virtualenv

    rm -rf $DEST/.venv
    virtualenv --system-site-packages $DEST/.venv
    source $DEST/.venv/bin/activate
    $DEST/.venv/bin/pip freeze > $DEST/requires-pre-pip
fi

if [[ "$USE_SYSTEMD" == "True" ]]; then
    pip_install_gr systemd-python
    # the default rate limit of 1000 messages / 30 seconds is not
    # sufficient given how verbose our logging is.
    iniset -sudo /etc/systemd/journald.conf "Journal" "RateLimitBurst" "0"
    sudo systemctl restart systemd-journald
fi



# Start Services
# ==============

# Check the status of running services
service_check

# Fin
# ===

set +o xtrace

if [[ -n "$LOGFILE" ]]; then
    exec 1>&3
    # Force all output to stdout and logs now
    exec 1> >( tee -a "${LOGFILE}" ) 2>&1
else
    # Force all output to stdout now
    exec 1>&3
fi

# Dump out the time totals
time_totals

# Warn that a deprecated feature was used
if [[ -n "$DEPRECATED_TEXT" ]]; then
    echo
    echo -e "WARNING: $DEPRECATED_TEXT"
    echo
fi

# Tell the user about using Systemd.

echo
echo "Services are running under systemd unit files."
echo

# Indicate how long this took to run (bash maintained variable ``SECONDS``)
echo_summary "stack.sh completed in $SECONDS seconds."


# Restore/close logging file descriptors
exec 1>&3
exec 2>&3
exec 3>&-
exec 6>&-
