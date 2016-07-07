# Notes on Firewall Setup

This page summarizes the ports used by BigchainDB and the traffic they should accept or reject, e.g. using a firewall or AWS security group.


## Inbound at Port 22

Port 22 is the default SSH port (TCP). It should expect unsolicited inbound traffic from arbitrary IP addresses.


## Inbound at Port 123

It you run an NTP daemon (client) on your BigchainDB node (and you should), then it shouldn't allow _all_ incoming UDP traffic on port 123 (the default NTP port). The only time it should allow incoming traffic on port 123 is if the NTP daemon sent a request to an external NTP server, and it's expecting a response from that server (i.e. established or related traffic). If you're using iptables for your firewall, then you should have an iptables rule allowing established, related traffic, something like:
```text
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
```

## Inbound at Port 8080

Port 8080 is the default port used by RethinkDB for its adminstrative web interface (TCP). While you _can_, you shouldn't allow traffic arbitrary external sources. You can still use the RethinkDB web interface by binding it to localhost and then accessing it via a SOCKS proxy or reverse proxy; see "Binding the web interface port" on [the RethinkDB page about securing your cluster](https://rethinkdb.com/docs/security/).


## Inbound at Port 9984

Port 9984 is the default port for the BigchainDB client-server API (TCP), which is served by Gunicorn HTTP Server.
It's _possible_ allow port 9984 to accept inbound traffic from anyone, but we recommend against doing that. Instead, set up a reverse proxy server (e.g. using Nginx) and only allow traffic from there. Information about how to do that can be found [in the Gunicorn documentation](http://docs.gunicorn.org/en/stable/deploy.html). (They call it a proxy.)

If Gunicorn and the reverse proxy are running on the same server, then you'll have to tell Gunicorn to listen on some port other than 9984 (so that the reverse proxy can listen on port 9984). You can do that by setting `server.bind` to 'localhost:PORT' in the [BigchainDB Configuration Settings](../nodes/configuration.html), where PORT is whatever port you chose (e.g. 9983).

You may want to have Gunicorn and the reverse proxy running on different servers, so that both can listen on port 9984. That would also help isolate the effects of a denial-of-service attack.


## Inbound at Port 28015

Port 28015 is the default port used by RethinkDB client driver connections (TCP). If your BigchainDB node is just one server, then Port 28015 only needs to listen on localhost, because all the client drivers will be running on localhost. Port 28015 doesn't need to accept inbound traffic from the outside world.


## Inbound at Port 29015

Port 29015 is the default port for RethinkDB intracluster connections (TCP). It should only accept incoming traffic from other RethinkDB servers in the cluster (a list of IP addresses that you should be able to find out).


## Inbound at Other Ports

Other ports you might need to consider include:

53 - The default DNS port (UDP) <br>
161 - The default SNMP port (usually UDP, sometimes TCP)

On Linux, you can use commands such as `netstat -tunlp` or `lsof -i` to get a sense of currently open/listening ports and connections, and the associated processes. 


## Outbound Traffic

If your node's firewall isn't allowing all outbound traffic, then it must at least allow outbound traffic on the above-mentioned ports.


## Cluster-Monitoring Server

If you set up a [cluster-monitoring server](../clusters-feds/monitoring.html) (running Telegraf, InfluxDB & Grafana), Telegraf will listen on port 8125 for UDP packets from StatsD, and the Grafana web dashboard will use port 3000. (Those are the default ports.)
