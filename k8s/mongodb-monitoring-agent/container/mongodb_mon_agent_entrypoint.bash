#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


set -euo pipefail
# -e Abort at the first failed line (i.e. if exit status is not 0)
# -u Abort when undefined variable is used
# -o pipefail (Bash-only) Piped commands return the status
#    of the last failed command, rather than the status of the last command

MONGODB_MON_CONF_FILE=/etc/mongodb-mms/monitoring-agent.config

mms_api_keyfile_path=`printenv MMS_API_KEYFILE_PATH`
mms_groupid_keyfile_path=`printenv MMS_GROUPID_KEYFILE_PATH`
ca_crt_path=`printenv CA_CRT_PATH`
monitoring_pem_path=`printenv MONITORING_PEM_PATH`

if [[ -z "${mms_api_keyfile_path:?MMS_API_KEYFILE_PATH not specified. Exiting!}" || \
    -z "${ca_crt_path:?CA_CRT_PATH not specified. Exiting!}" || \
    -z "${monitoring_pem_path:?MONITORING_PEM_PATH not specified. Exiting!}" || \
    -z "${mms_groupid_keyfile_path:?MMS_GROUPID_KEYFILE_PATH not specified. Exiting!}" ]];then
  exit 1
else
  echo MMS_API_KEYFILE_PATH="$mms_api_keyfile_path"
  echo MMS_GROUPID_KEYFILE_PATH="$mms_groupid_keyfile_path"
  echo CA_CRT_PATH="$ca_crt_path"
  echo MONITORING_PEM_PATH="$monitoring_pem_path"
fi

# Delete the line containing "mmsApiKey" and the line containing "mmsGroupId"
# in the MongoDB Monitoring Agent config file
# /etc/mongodb-mms/monitoring-agent.config
sed -i '/mmsApiKey/d'  $MONGODB_MON_CONF_FILE
sed -i '/mmsGroupId/d'  $MONGODB_MON_CONF_FILE

# Get the api key from file
mms_api_key=`cat ${mms_api_keyfile_path}`
mms_groupid_key=`cat ${mms_groupid_keyfile_path}`

# Append a new line of the form
# mmsApiKey=value_of_MMS_API_KEY
echo "mmsApiKey="${mms_api_key} >> ${MONGODB_MON_CONF_FILE}
echo "mmsGroupId="${mms_groupid_key} >> ${MONGODB_MON_CONF_FILE}

# Append SSL settings to the config file
echo "useSslForAllConnections=true" >> ${MONGODB_MON_CONF_FILE}
echo "sslRequireValidServerCertificates=true" >> ${MONGODB_MON_CONF_FILE}
echo "sslTrustedServerCertificates="${ca_crt_path} >> ${MONGODB_MON_CONF_FILE}
echo "sslClientCertificate="${monitoring_pem_path} >> ${MONGODB_MON_CONF_FILE}
echo "#sslClientCertificatePassword=<password>" >> ${MONGODB_MON_CONF_FILE}

# start mdb monitoring agent
echo "INFO: starting mdb monitor..."
exec mongodb-mms-monitoring-agent \
    --conf $MONGODB_MON_CONF_FILE \
    --loglevel debug
