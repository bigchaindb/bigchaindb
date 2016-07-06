# Notes on Firewall Setup

When you set up the firewall (or security group on AWS) for a BigchainD node, here is a list of the ports where _unsolicited_ inbound traffic is expected:

22 - The default SSH port (TCP) <br>
8080 - The default port for the RethinkDB web interface (TCP) <br>
9984 - The default port for the BigchainDB client-server API (TCP) <br>
28015 - The default port for RethinkDB client driver connections (TCP) <br>
29015 - The default port for RethinkDB intracluster connections (TCP)

It you run an NTP daemon (client) on your BigchainDB node (and you should), then it shouldn't allow _all_ incoming UDP traffic on port 123 (the default NTP port). The only time it should allow incoming traffic on port 123 is if the NTP daemon sent a request to an external NTP server, and it's expecting a response from that server (i.e. established or related traffic). If you're using iptables for your firewall, then you should have an iptables rule allowing established, related traffic, something like:
```text
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
```

Other ports you might need to consider include:

53 - The default DNS port (UDP) <br>
161 - The default SNMP port (usually UDP, sometimes TCP)

If your node's firewall isn't allowing all outbound traffic, then it must at least allow outbound traffic on the above-mentioned ports (including port 123 for NTP).

Aside: If you set up a [cluster-monitoring server](../clusters-feds/monitoring.html) (running Telegraf, InfluxDB & Grafana), Telegraf will listen on port 8125 for UDP packets from StatsD, and the Grafana web dashboard will use port 3000. (Those are the default ports.)