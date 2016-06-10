# Monitoring

BigchainDB uses [StatsD](https://github.com/etsy/statsd) for monitoring. We require some additional infrastructure to take full advantage of its functionality:

* an agent to listen for metrics: [Telegraf](https://github.com/influxdata/telegraf),
* a time-series database: [InfluxDB](https://influxdata.com/time-series-platform/influxdb/), and
* a frontend to display analytics: [Grafana](http://grafana.org/).

We put each of those inside its own Docker container. The whole system is illustrated below.

![BigchainDB monitoring system diagram: Application metrics flow from servers running BigchainDB to Telegraf to InfluxDB to Grafana](../_static/monitoring_system_diagram.png)

For ease of use, we've created a Docker [_Compose file_](https://docs.docker.com/compose/compose-file/) (named `docker-compose-monitor.yml`) to define the monitoring system setup. To use it, just go to to the top `bigchaindb` directory and run:
```text
$ docker-compose -f docker-compose-monitor.yml build
$ docker-compose -f docker-compose-monitor.yml up
```

It is also possible to mount a host directory as a data volume for InfluxDB
by setting the `INFLUXDB_DATA` environment variable:
```text
$ INFLUXDB_DATA=/data docker-compose -f docker-compose-monitor.yml up
```

You can view the Grafana dashboard in your web browser at:

[http://localhost:3000/dashboard/script/bigchaindb_dashboard.js](http://localhost:3000/dashboard/script/bigchaindb_dashboard.js)

(You may want to replace `localhost` with another hostname in that URL, e.g. the hostname of a remote monitoring server.)

The login and password are `admin` by default. If BigchainDB is running and processing transactions, you should see analytics—if not, [start BigchainDB](installing-server.html#run-bigchaindb) and load some test transactions:
```text
$ bigchaindb load
```

then refresh the page after a few seconds.

If you're not interested in monitoring, don't worry: BigchainDB will function just fine without any monitoring setup.

Feel free to modify the [custom Grafana dashboard](https://github.com/rhsimplex/grafana-bigchaindb-docker/blob/master/bigchaindb_dashboard.js) to your liking!
