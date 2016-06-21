# Timestamps in BigchainDB

Each transaction, block and vote has an associated timestamp.

Interpreting those timestamps is tricky. If there's one message to take away from this section, it is this: you need to look at multiple timestamps from multiple sources to get some idea of when something happened.


## Timestamp Sources

A transaction's timestamp is provided by the client which created and submitted the transaction to a BigchainDB node. A block's timestamp is provided by the BigchainDB node which created the block. A vote's timestamp is provided by the BigchainDB node which created the vote.

When a BigchainDB client or node needs a timestamp, it calls a BigchainDB utility function named `timestamp()`. There's a detailed explanation of how that function works below, but the bottom line is that it gets the Unix time from the system clock, rounded to the nearest second.

Unix time is defined as defined as the number of seconds that have elapsed since 00:00:00 Coordinated Universal Time (UTC), Thursday, 1 January 1970 (i.e. since the Unix Epoch), _not counting leap seconds_. There are more details in [the Wikipedia article about Unix time](https://en.wikipedia.org/wiki/Unix_time).


## How to Interpret Timestamps

If a client or node's system clock is wrong, then its timestamps will be wrong. That's not the end of the world, though, because you can look at many timestamps to get an idea of when something happened. For example, a transaction in a decided-valid block has many associated timestamps:

* its own timestamp
* the timestamps of the other transactions in the block; there could be as many as 999 of those
* the timestamp of the block
* the timestamps of all the votes on the block

Those timestamps come from many sources, so you can look at all of them to get some statistical sense of when the transaction "actually happened." The timestamp of the block should always be after the timestamp of the transaction, and the timestamp of the votes should always be after the timestamp of the block.


## Syncing with Standard Clocks

A client or node can run an NTP daemon to keep its system clock in sync with standard clocks. There's more information about that in the section titled [Sync Your System Clock](../nodes/setup-run-node.html#sync-your-system-clock).


## Converting Timestamps to UTC

It's not always possible to convert a Unix time to a UTC time, because Unix time doesn't have leap seconds, but UTC does. That means that there are some Unix times which correspond to two different UTC times, and there are other Unix times which don't correspond to any UTC time. Be suspicious of any function which claims to convert Unix time to UTC time. It's possible, but to be correct, it would have to give two answers for some Unix times, and errors for other Unix times.

Leap seconds are rare, so it's usually not a problem to convert a Unix time to a UTC time; just check the converter that you're using to make sure that it's got some sophistication.


## Including Trusted Timestamps

If you want to create a transaction payload with a trusted timestamp, you can.

One way to do that would be to send a payload to a trusted timestamping service. They will send back a timestamp, a signature, and their public key. They should also explain how you can verify the signature. You can then include the original payload, the timestamp, the signature, and the service's public key in your transaction. That way, anyone can verify that the original payload was signed by the trusted timestamping service.


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

(If `clock_gettime()` is not available or returns with a nonzero exit code, it falls back to `_PyTime_gettimeofday_info()`, which is a wrapper around [gettimeofday()](http://man7.org/linux/man-pages/man2/gettimeofday.2.html), an older function that was marked obsolete in POSIX.1-2008.)
