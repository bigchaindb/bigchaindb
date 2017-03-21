# Dockerfile for MongoDB Monitoring Agent
# Use it to create bigchaindb/mongodb-monitoring-agent
# on Docker Hub.

# "Never install the Monitoring Agent on the same server as a data bearing mongod instance."
# More help:
# https://docs.cloudmanager.mongodb.com/tutorial/install-monitoring-agent-with-deb-package/

FROM ubuntu:16.04
LABEL maintainer "dev@bigchaindb.com"
ENV REFRESHED_AT 2017-03-13
# Using ARG, one can set DEBIAN_FRONTEND=noninteractive and others
# just for the duration of the build:
ARG DEBIAN_FRONTEND=noninteractive
ARG DEB_FILE=mongodb-mms-monitoring-agent_latest_amd64.ubuntu1604.deb
ARG FILE_URL="https://cloud.mongodb.com/download/agent/"$DEB_FILE

# Download the Monitoring Agent as a .deb package and install it
WORKDIR /
RUN apt update && \
    apt upgrade && \
    apt autoremove && \
    curl -OLsS $FILE_URL && \
    dpkg -i $DEB_FILE && \
    rm -f $DEB_FILE && \
    apt clean

# The above installation puts a default config file in
# /etc/mongodb-mms/monitoring-agent.config
# It should contain a line like: "mmsApiKey="
# i.e. with no value specified.
# We need to set that value to the "agent API key" value from Cloud Manager,
# but of course that value varies from user to user,
# so we can't hard-code it into the Docker image.

# Kubernetes can set an MMS_API_KEY environment variable
# in the container
# (including from Secrets or ConfigMaps)
# An entrypoint bash script can then use the value of MMS_API_KEY
# to write the mmsApiKey value in the config file
# /etc/mongodb-mms/monitoring-agent.config
# before running the MongoDB Monitoring Agent.

# The MongoDB Monitoring Agent has other
# config settings besides mmsApiKey,
# but it's the only one that *must* be set. See:
# https://docs.cloudmanager.mongodb.com/reference/monitoring-agent/

# ?? USER mongodb-mms-agent
COPY mon-agent-entrypoint.sh /
RUN chmod +x /mon-agent-entrypoint.sh
ENTRYPOINT ["/mon-agent-entrypoint.sh"]
 