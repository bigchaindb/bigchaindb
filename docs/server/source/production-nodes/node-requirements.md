# Production Node Requirements

**This page is about the requirements of BigchainDB Server.** You can find the requirements of MongoDB, NGINX, your NTP daemon, your monitoring software, and other [production node components](node-components.html) in the documentation for that software.


## OS Requirements

BigchainDB Server requires Python 3.4+ and Python 3.4+ [will run on any modern OS](https://docs.python.org/3.4/using/index.html), but we recommend using an LTS version of [Ubuntu Server](https://www.ubuntu.com/server) or a similarly server-grade Linux distribution.

_Don't use macOS_ (formerly OS X, formerly Mac OS X), because it's not a server-grade operating system. Also, BigchaindB Server uses the Python multiprocessing package and [some functionality in the multiprocessing package doesn't work on Mac OS X](https://docs.python.org/3.4/library/multiprocessing.html#multiprocessing.Queue.qsize).


## General Considerations

BigchainDB Server runs many concurrent processes, so more RAM and more CPU cores is better.

As mentioned on the page about [production node components](node-components.html), every machine running BigchainDB Server should be running an NTP daemon.
