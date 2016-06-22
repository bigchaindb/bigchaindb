# Notes on NTP Daemon Setup

There are several NTP daemons available, including:

* The reference NTP daemon (`ntpd`) from ntp.org; see [their support website](http://support.ntp.org/bin/view/Support/WebHome)
* [chrony](https://chrony.tuxfamily.org/index.html)
* [OpenNTPD](http://www.openntpd.org/)
* Maybe [NTPsec](https://www.ntpsec.org/), once it's production-ready
* Maybe [Ntimed](http://nwtime.org/projects/ntimed/), once it's production-ready
* [More](https://en.wikipedia.org/wiki/Ntpd#Implementations)

We suggest you run your NTP daemon in a mode which steps the system clock back by one second when a leap second occurs, rather than using one of the fancy "slewing" or "smearing" options. That's the default with `ntpd` and `chronyd`. (Aside: There's [an interesting blog post by Red Hat](http://developers.redhat.com/blog/2015/06/01/five-different-ways-handle-leap-seconds-ntp/) about the various ways to handle leap seconds.)

It's tricky to make an NTP daemon setup secure. Always install the latest version and read the documentation about how to configure and run it securely.


## Ubuntu Packages

The [Ubuntu 14.04 (Trusty Tahr) package `ntp`](https://launchpad.net/ubuntu/trusty/+source/ntp) is based on the reference implementation of an NTP daemon.

The following commands will uninstall the `ntp` and `ntpdate` packages, install the latest `ntp` package (which _might not be based on the latest ntpd code_), and start the NTP daemon (a local NTP server). (`ntpdate` is not reinstalled because it's [deprecated](https://askubuntu.com/questions/297560/ntpd-vs-ntpdate-pros-and-cons) and you shouldn't use it.)
```text
sudo apt-get --purge remove ntp ntpdate
sudo apt-get autoremove
sudo apt-get update
sudo apt-get install ntp
# That should start the NTP daemon too, but just to be sure:
sudo service ntp restart
```

You can check if NTP is running using `sudo ntpq -p`.

You may want to use different NTP time servers. You can change them by editing the NTP config file `/etc/ntp.conf`.

Note: A server running the NTP daemon can be used by others for DRDoS amplification attacks. The above installation procedure should install a default NTP configuration file `/etc/ntp.conf` with the lines:
```text
restrict -4 default kod notrap nomodify nopeer noquery
restrict -6 default kod notrap nomodify nopeer noquery
```

Those lines should prevent the NTP daemon from being used in an attack. (The first line is for IPv4, the second for IPv6.)

There are additional things you can do to make NTP more secure. See the [NTP Support Website](http://support.ntp.org/bin/view/Support/WebHome) for more details.
