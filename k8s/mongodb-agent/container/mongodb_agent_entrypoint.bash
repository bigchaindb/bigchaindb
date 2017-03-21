#!/bin/bash

set -euo pipefail
# -e Abort at the first failed line (i.e. if exit status is not 0)
# -u Abort when undefined variable is used
# -o pipefail (Bash-only) Piped commands return the status
#    of the last failed command, rather than the status of the last command

# Delete all lines containing "mmsApiKey"
# in the MongoDB Monitoring Agent config file 
# /etc/mongodb-mms/monitoring-agent.config
sed -i '/mmsApiKey/d'  /etc/mongodb-mms/monitoring-agent.config

# Append a new line of the form
# mmsApiKey=value_of_MMS_API_KEY
echo "mmsApiKey="$MMS_API_KEY >> /etc/mongodb-mms/monitoring-agent.config

# Start MongoDB Monitoring Agent as a service
systemctl start mongodb-mms-monitoring-agent.service
