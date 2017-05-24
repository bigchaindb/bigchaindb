#!/bin/bash

set -euo pipefail
# -e Abort at the first failed line (i.e. if exit status is not 0)
# -u Abort when undefined variable is used
# -o pipefail (Bash-only) Piped commands return the status
#    of the last failed command, rather than the status of the last command

MONGODB_MON_CONF_FILE=/etc/mongodb-mms/monitoring-agent.config

mms_api_key=`printenv MMS_API_KEY`
ca_crt_path=`printenv CA_CRT_PATH`
monitoring_crt_path=`printenv MONITORING_PEM_PATH`

if [[ -z "${mms_api_key}" || \
    -z "${ca_crt_path}" || \
    -z "${monitoring_crt_path}" ]]; then
  echo "Invalid environment settings detected. Exiting!"
  exit 1
fi

# Delete all lines containing "mmsApiKey" in the MongoDB Monitoring Agent
# config file /etc/mongodb-mms/monitoring-agent.config
sed -i '/mmsApiKey/d'  $MONGODB_MON_CONF_FILE

# Append a new line of the form
# mmsApiKey=value_of_MMS_API_KEY
echo "mmsApiKey="${mms_api_key} >> ${MONGODB_MON_CONF_FILE}

# Append SSL settings to the config file
echo "useSslForAllConnections=true" >> ${MONGODB_MON_CONF_FILE}
echo "sslRequireValidServerCertificates=true" >> ${MONGODB_MON_CONF_FILE}
echo "sslTrustedServerCertificates="${ca_crt_path} >> ${MONGODB_MON_CONF_FILE}
echo "sslClientCertificate="${monitoring_crt_path} >> ${MONGODB_MON_CONF_FILE}
echo "#sslClientCertificatePassword=<password>" >> ${MONGODB_MON_CONF_FILE}

# start mdb monitoring agent
echo "INFO: starting mdb monitor..."
exec mongodb-mms-monitoring-agent \
    --conf $MONGODB_MON_CONF_FILE \
    --loglevel debug
