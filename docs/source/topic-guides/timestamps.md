# Timestamps in BigchainDB

Each transaction, block and vote has an associated timestamp.

Interpreting those timestamps is tricky, hence the need for this section.


## Timestamp Sources

A transaction's timestamp is provided by the client which created and submitted the transaction to a BigchainDB node. A block's timestamp is provided by the BigchainDB node which created the block. A vote's timestamp is provided by the BigchainDB node which created the vote.

When a BigchainDB client or node needs a timestamp, it calls a BigchainDB utility function named `timestamp()`. There's a detailed explanation of how that function works below, but the short version is that it gets the [Unix time](https://en.wikipedia.org/wiki/Unix_time) from the system clock, rounded to the nearest second.

[Unix time](https://en.wikipedia.org/wiki/Unix_time) is defined as defined as the number of seconds that have elapsed since 00:00:00 Coordinated Universal Time (UTC), Thursday, 1 January 1970 (i.e. since the Unix Epoch), _not counting leap seconds_.


## System Clock Accuracy

We can't say anything about the accuracy client system clocks (i.e. used to generate the timestamps for transactions). They're still potentially useful, however, in a statistical sense. We say more about that below.

We advise BigchainDB nodes to run special software (an "NTP daemon") to keep their system clock in sync with standard time servers. That sounds great, but there's a gotcha. NTP uses [UTC (Coordinated Universal Time)](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) and UTC has [leap seconds](https://en.wikipedia.org/wiki/Leap_second), but Unix time ignores leap seconds.

A leap second is an extra second added to the end of some days. On a leap second, the UTC time goes from 23:59:59 UTC to 23:59:60 UTC (instead of 00:00:00 UTC like usual).
There's [a nice blog post by Red Hat](http://developers.redhat.com/blog/2015/06/01/five-different-ways-handle-leap-seconds-ntp/) about what happens when a leap second arrives via NTP:

> "When a leap second is inserted to UTC, the system clock skips that second [23:59:60] as it can’t be represented and is suddenly ahead of UTC by one second. There are several ways how the clock can be corrected."

> "The most common approach is to simply step the clock back by one second when the clock gets to 00:00:00 UTC. This is implemented in the Linux kernel and it is enabled by default when the clock is synchronized with NTP servers by the ntpd or chronyd daemon from the reference or chrony NTP implementations respectively."

> "... There will be a backward step, but the clock will be off only for one second."

We suggest that BigchainDB nodes run their NTP daemon in a mode which steps the system clock back by one second when a leap second occurs, rather than using one of the fancy "slewing" or "smearing" options. That way, there's only a small set of ambiguous timestamps (i.e. the ones associated with leap seconds).


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


## Converting Timestamps to UTC

It's not always possible to convert a Unix time to a UTC time, because Unix time doesn't have leap seconds, but UTC does. That means that there are some Unix times which correspond to two different UTC times. Be suspicious of any function which claims to convert Unix time to UTC time. It's possible, but to be correct, it would have to give two answers for some Unix times.

Leap seconds are rare, so it's usually not a problem to convert a Unix time to a UTC time; just check the converter that you're using to make sure that it's got some sophistication.


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
