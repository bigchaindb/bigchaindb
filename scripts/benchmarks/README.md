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

    $ COMPOSE_PROJECT_NAME=somename python3 scripts/bench_create.py

### Results
