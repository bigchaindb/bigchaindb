<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Production Node Security & Privacy

Here are some references about how to secure an Ubuntu 18.04 server:

- [Ubuntu 18.04 - Ubuntu Server Guide - Security](https://help.ubuntu.com/lts/serverguide/security.html.en)
- [Ubuntu Blog: National Cyber Security Centre publish Ubuntu 18.04 LTS Security Guide](https://blog.ubuntu.com/2018/07/30/national-cyber-security-centre-publish-ubuntu-18-04-lts-security-guide)

Also, here are some recommendations a node operator can follow to enhance the privacy of the data coming to, stored on, and leaving their node:

- Ensure that all data stored on a node is encrypted at rest, e.g. using full disk encryption. This can be provided as a service by the operating system, transparently to BigchainDB, MongoDB and Tendermint.
- Ensure that all data is encrypted in transit, i.e. enforce using HTTPS for the HTTP API and the Websocket API. This can be done using NGINX or similar, as we do with the BigchainDB Testnet.
