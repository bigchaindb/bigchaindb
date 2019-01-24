<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Notes for Firewall Setup

This is a page of notes on the ports potentially used by BigchainDB nodes and the traffic they should expect, to help with firewall setup (or security group setup on cloud providers). This page is _not_ a firewall tutorial or step-by-step guide.

## Expected Unsolicited Inbound Traffic

The following ports should expect unsolicited inbound traffic:

1. **Port 22** can expect inbound SSH (TCP) traffic from the node administrator (i.e. a small set of IP addresses).
1. **Port 9984** can expect inbound HTTP (TCP) traffic from BigchainDB clients sending transactions to the BigchainDB HTTP API.
1. **Port 9985** can expect inbound WebSocket traffic from BigchainDB clients.
1. **Port 26656** can expect inbound Tendermint P2P traffic from other Tendermint peers.
1. **Port 9986** can expect inbound HTTP (TCP) traffic from clients accessing the Public Key of a Tendermint instance.

All other ports should only get inbound traffic in response to specific requests from inside the node.

## Port 22

Port 22 is the default SSH port (TCP) so you'll at least want to make it possible to SSH in from your remote machine(s).

## Port 53

Port 53 is the default DNS port (UDP). It may be used, for example, by some package managers when look up the IP address associated with certain package sources.

## Port 80

Port 80 is the default HTTP port (TCP). It's used by some package managers to get packages. It's _not_ the default port for the BigchainDB client-server HTTP API.

## Port 123

Port 123 is the default NTP port (UDP). You should be running an NTP daemon on production BigchainDB nodes. NTP daemons must be able to send requests to external NTP servers and accept the respones.

## Port 161

Port 161 is the default SNMP port (usually UDP, sometimes TCP). SNMP is used, for example, by some server monitoring systems.

## Port 443

Port 443 is the default HTTPS port (TCP). Package managers might also get some packages using HTTPS.

## Port 9984

Port 9984 is the default port for the BigchainDB client-server HTTP API (TCP), which is served by Gunicorn HTTP Server. It's _possible_ allow port 9984 to accept inbound traffic from anyone, but we recommend against doing that. Instead, set up a reverse proxy server (e.g. using Nginx) and only allow traffic from there. Information about how to do that can be found [in the Gunicorn documentation](http://docs.gunicorn.org/en/stable/deploy.html). (They call it a proxy.)

If Gunicorn and the reverse proxy are running on the same server, then you'll have to tell Gunicorn to listen on some port other than 9984 (so that the reverse proxy can listen on port 9984). You can do that by setting `server.bind` to 'localhost:PORT' in the [BigchainDB Configuration Settings](../server-reference/configuration), where PORT is whatever port you chose (e.g. 9983).

You may want to have Gunicorn and the reverse proxy running on different servers, so that both can listen on port 9984. That would also help isolate the effects of a denial-of-service attack.

## Port 9985

Port 9985 is the default port for the BigchainDB WebSocket Event Stream API.

## Port 9986

Port 9986 is the default port to access the Public Key of a Tendermint instance, it is used by a NGINX instance
that runs with Tendermint instance(Pod), and only hosts the Public Key.

## Port 26656

Port 26656 is the default port used by Tendermint Core to communicate with other instances of Tendermint Core (peers).

## Port 26657

Port 26657 is the default port used by Tendermint Core for RPC traffic. BigchainDB nodes use that internally; they don't expect incoming traffic from the outside world on port 26657.

## Port 26658

Port 26658 is the default port used by Tendermint Core for ABCI traffic. BigchainDB nodes use that internally; they don't expect incoming traffic from the outside world on port 26658.

## Other Ports

On Linux, you can use commands such as `netstat -tunlp` or `lsof -i` to get a sense of currently open/listening ports and connections, and the associated processes. 
