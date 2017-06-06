# Benchmarks

## CREATE transaction throughput

This is a measurement of the throughput of CREATE transactions through the entire
pipeline, ie, the web frontend, block creation, and block validation, where the
output of the measurement is transactions per second.

The benchmark runs for a fixed period of time and makes metrics available via
a graphite interface.

### Running the benchmark

Dependencies:

* Python 3.5+
* docker-compose 1.8.0+
* docker 1.12+

To start:

    $ python3 scripts/benchmarks/create_thoughtput.py

To start using a separate namespace for docker-compose:

    $ COMPOSE_PROJECT_NAME=somename python3 scripts/benchmarks/create_thoughtput.py

### Results

A test was run on AWS with the following instance configuration:

* Ubuntu Server 16.04 (ami-060cde69)
* 32 core compute optimized (c3.8xlarge)
* 100gb root volume (300/3000 IOPS)

The server received and validated over 800 transactions per second:

![BigchainDB transaction throughput](https://cloud.githubusercontent.com/assets/125019/26688641/85d56d1e-46f3-11e7-8148-bf3bc8c54c33.png)

For more information on how the benchmark was run, the abridged session buffer [is available](https://gist.github.com/libscott/8a37c5e134b2d55cfb55082b1cd85a02).
