# It might be better to:
# 1. start by only allowing SSH on port 22 (in the security group)
# 2. use SSH to set up a proper firewall on the (virtual) machine
# 3. add a second security group with more ports open

resource "aws_security_group" "node_sg1" {
  name_prefix = "BigchainDB_"
  description = "Single-machine BigchainDB node security group"
  tags = {
    Name = "BigchainDB_one-m"
  }

  # Allow all outbound traffic
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # DNS
  ingress {
    from_port = 53
    to_port = 53
    protocol = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP is used by some package managers
  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # NTP daemons use port 123 but the request will
  # come from inside the firewall so a response is expected

  # SNMP (e.g. for server monitoring)
  ingress {
    from_port = 161
    to_port = 161
    protocol = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS is used when installing RethinkDB
  # and by some package managers
  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # StatsD
  ingress {
    from_port = 8125
    to_port = 8125
    protocol = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Future: Don't allow port 8080 for the RethinkDB web interface.
  # Use a SOCKS proxy or reverse proxy instead.

  ingress {
    from_port = 8080
    to_port = 8080
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # BigchainDB Client-Server REST API
  ingress {
    from_port = 9984
    to_port = 9984
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Port 28015 doesn't have to be open to the outside
  # since the RethinkDB client and server are on localhost

  # RethinkDB intracluster communications use port 29015
  ingress {
    from_port = 29015
    to_port = 29015
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
