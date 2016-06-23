# Timestamps in BigchainDB

Each transaction, block and vote has an associated timestamp. Interpreting those timestamps is tricky, hence the need for this section.


## Timestamp Sources & Accuracy

A transaction's timestamp is provided by the client which created and submitted the transaction to a BigchainDB node. A block's timestamp is provided by the BigchainDB node which created the block. A vote's timestamp is provided by the BigchainDB node which created the vote.

When a BigchainDB client or node needs a timestamp, it calls a BigchainDB utility function named `timestamp()`. There's a detailed explanation of how that function works below, but the short version is that it gets the [Unix time](https://en.wikipedia.org/wiki/Unix_time) from its system clock, rounded to the nearest second.

We can't say anything about the accuracy of the system clock on clients. Timestamps from clients are still potentially useful, however, in a statistical sense. We say more about that below.

We advise BigchainDB nodes to run special software (an "NTP daemon") to keep their system clock in sync with standard time servers.


## Converting Timestamps to UTC

To convert a BigchainDB timestamp (a Unix time) to UTC, you need to know how the node providing the timestamp was maintaining its system clock (which is the source of its timestamps). In particular, you need to know how it was handling leap seconds. It turns out there are many ways to handle leap seconds. There's [a nice Red Hat Developer Blog post about the various options](http://developers.redhat.com/blog/2015/06/01/five-different-ways-handle-leap-seconds-ntp/):

> "When a leap second is inserted to UTC, the system clock skips that second [23:59:60] as it can’t be represented and is suddenly ahead of UTC by one second. There are several ways how the clock can be corrected."

> "The most common approach is to simply step the clock back by one second when the clock gets to 00:00:00 UTC. This is implemented in the Linux kernel and it is enabled by default when the clock is synchronized with NTP servers by the ntpd or chronyd daemon from the reference or chrony NTP implementations respectively."

> "... There will be a backward step, but the clock will be off only for one second."

We suggest that BigchainDB nodes run their NTP daemon in a mode which tells the kernel to step the system clock back by one second when a leap second occurs, rather than using one of the fancy "slewing" or "smearing" options. That way, there's only a small set of ambiguous timestamps (i.e. the ones associated with leap seconds).

The result is that some timestamps can't be converted unambigously to a single UTC timestamp, but that only happens for leap seconds, and leap seconds are rare. (Only 26 had been inserted between 1972 and the end of 2015.)

**So long as you avoid the leap seconds, you can convert BigchainDB timestamps (Unix time timestamps) to UTC unambiguosly using any standard conversion tool or library function.**

There's [a list of all the leap seconds on Wikipedia](https://en.wikipedia.org/wiki/Leap_second).

There's another gotcha with (Unix time) timestamps: you can't calculate the real-world elapsed time between two timestamps (correctly) by subtracting the smaller timestamp from the larger one. The result won't include any of the leap seconds that occured between the two timestamps. You could look up how many leap seconds happened between the two timestamps and add that to the result. There are many library functions for working with timestamps; those are beyond the scope of this documentation.


## Using Timestamps

You can look at many timestamps to get a statistical sense of when something happened. For example, a transaction in a decided-valid block has many associated timestamps:

* its own timestamp
* the timestamps of the other transactions in the block; there could be as many as 999 of those
* the timestamp of the block
* the timestamps of all the votes on the block

Those timestamps come from many sources, so you can look at all of them to get some statistical sense of when the transaction "actually happened." The timestamp of the block should always be after the timestamp of the transaction, and the timestamp of the votes should always be after the timestamp of the block.


## How BigchainDB Uses Timestamps

BigchainDB _doesn't_ use timestamps to determine the order of transactions or blocks. In particular, the order of blocks is determined by RethinkDB's changefeed on the bigchain table.

BigchainDB does use timestamps for some things. It uses them to determine if a transaction has been waiting in the backlog for too long (i.e. because the node assigned to it hasn't handled it yet). It also uses timestamps to determine the status of timeout conditions (used by escrow).


## Including Trusted Timestamps

If you want to create a transaction payload with a trusted timestamp, you can.

One way to do that would be to send a payload to a trusted timestamping service. They will send back a timestamp, a signature, and their public key. They should also explain how you can verify the signature. You can then include the original payload, the timestamp, the signature, and the service's public key in your transaction. That way, anyone with the verification instructions can verify that the original payload was signed by the trusted timestamping service.


## How the timestamp() Function Works

BigchainDB has a utility function named `timestamp()` which amounts to:
```python
timestamp() = str(round(time.time()))
```

In other words, it calls the `time()` function in Python's `time` module, rounds that to the nearest integer, and converts the result to a string.

It rounds the output of `time.time()` to the nearest second because, according to [the Python documentation for `time.time()`](https://docs.python.org/3.4/library/time.html#time.time), "...not all systems provide time with a better precision than 1 second."

How does `time.time()` work? If you look in the C source code, it calls `floattime()` and `floattime()` calls [clock_gettime()](https://www.cs.rutgers.edu/~pxk/416/notes/c-tutorials/gettime.html), if it's available.
```text
ret = clock_gettime(CLOCK_REALTIME, &tp);
```

With `CLOCK_REALTIME` as the first argument, it returns the Unix time as described above.


## Why Not Use UTC, TAI or Something Unambiguous for Timestamps?

*nix system clocks, and the library functions to access them, use Unix time (also called POSIX time), not UTC, TAI, or something unambiguous. There are many nonstandard and uncommon ways to get an unambiguous time, but we opted to use something standard. Unix time is only problematic for leap seconds, and those are rare. All other times are represented uniquely.
