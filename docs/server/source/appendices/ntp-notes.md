<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Notes on NTP Daemon Setup

There are several NTP daemons available, including:

* The reference NTP daemon (`ntpd`) from ntp.org; see [their support website](http://support.ntp.org/bin/view/Support/WebHome)
* [chrony](https://chrony.tuxfamily.org/index.html)
* [OpenNTPD](http://www.openntpd.org/)
* Maybe [NTPsec](https://www.ntpsec.org/), once it's production-ready
* Maybe [Ntimed](http://nwtime.org/projects/ntimed/), once it's production-ready
* [More](https://en.wikipedia.org/wiki/Ntpd#Implementations)

We suggest you run your NTP daemon in a mode which will tell your OS kernel to handle leap seconds in a particular way: the default NTP way, so that system clock adjustments are localized and not spread out across the minutes, hours, or days surrounding leap seconds (e.g. "slewing" or "smearing"). There's [a nice Red Hat Developer Blog post about the various options](https://developers.redhat.com/blog/2015/06/01/five-different-ways-handle-leap-seconds-ntp/).

Use the default mode with `ntpd` and `chronyd`. For another NTP daemon, consult its documentation.

It's tricky to make an NTP daemon setup secure. Always install the latest version and read the documentation about how to configure and run it securely. See the [notes on firewall setup](firewall-notes).


## Amazon Linux Instances

If your BigchainDB node is running on an Amazon Linux instance (i.e. a Linux instance packaged by Amazon, not Canonical, Red Hat, or someone else), then an NTP daemon should already be installed and configured. See the EC2 documentation on [Setting the Time for Your Linux Instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html).

That said, you should check _which_ NTP daemon is installed. Is it recent? Is it configured securely?


## The Ubuntu ntp Packages

The [Ubuntu `ntp` packages](https://launchpad.net/ubuntu/+source/ntp) are based on the reference implementation of NTP.

The following commands will uninstall the `ntp` and `ntpdate` packages, install the latest `ntp` package (which _might not be based on the latest ntpd code_), and start the NTP daemon (a local NTP server). (`ntpdate` is not reinstalled because it's [deprecated](https://askubuntu.com/questions/297560/ntpd-vs-ntpdate-pros-and-cons) and you shouldn't use it.)
```text
sudo apt-get --purge remove ntp ntpdate
sudo apt-get autoremove
sudo apt-get update
sudo apt-get install ntp
# That should start the NTP daemon too, but just to be sure:
sudo service ntp restart
```

You can check if `ntpd` is running using `sudo ntpq -p`.

You may want to use different NTP time servers. You can change them by editing the NTP config file `/etc/ntp.conf`.

Note: A server running an NTP daemon can be used by others for DRDoS amplification attacks. The above installation procedure should install a default NTP configuration file `/etc/ntp.conf` with the lines:
```text
restrict -4 default kod notrap nomodify nopeer noquery
restrict -6 default kod notrap nomodify nopeer noquery
```

Those lines should prevent the NTP daemon from being used in an attack. (The first line is for IPv4, the second for IPv6.)

There are additional things you can do to make NTP more secure. See the [NTP Support Website](http://support.ntp.org/bin/view/Support/WebHome) for more details.
