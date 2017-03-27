#!/bin/bash

set -euo pipefail
# -e Abort at the first failed line (i.e. if exit status is not 0)
# -u Abort when undefined variable is used
# -o pipefail (Bash-only) Piped commands return the status
#    of the last failed command, rather than the status of the last command

MONGODB_MON_CONF_FILE=/etc/mongodb-mms/monitoring-agent.config

mms_api_key=`printenv MMS_API_KEY`

if [[ -z "${mms_api_key}" ]]; then
  echo "Invalid environment settings detected. Exiting!"
  exit 1
fi

# Delete all lines containing "mmsApiKey" in the MongoDB Monitoring Agent
# config file /etc/mongodb-mms/monitoring-agent.config
sed -i '/mmsApiKey/d'  $MONGODB_MON_CONF_FILE

# Append a new line of the form
# mmsApiKey=value_of_MMS_API_KEY
echo "mmsApiKey="${mms_api_key} >> $MONGODB_MON_CONF_FILE

# start mdb monitoring agent
echo "INFO: starting mdb monitor..."
exec mongodb-mms-monitoring-agent \
    --conf $MONGODB_MON_CONF_FILE \
    --loglevel debug
