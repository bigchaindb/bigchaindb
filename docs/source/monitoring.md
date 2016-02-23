# Monitoring

BigchainDB uses [statsd](https://github.com/etsy/statsd) for monitoring.  To fully take advantage of this functionality requires some additional infrastructure: an agent to listen for metrics (e.g. [telegraf](https://github.com/influxdata/telegraf)), a time-series database (e.g. [influxdb](https://influxdata.com/time-series-platform/influxdb/), and a frontend to display analytics (e.g. [Grafana](http://grafana.org/)).

For ease of use, we've provided a docker compose file that sets up all these services for testing. Simply run in the BigchainDB directory:

```text
$ docker-compose -f docker-compose-monitor.yml build
$ docker-compose -f docker-compose-monitor.yml up
```

and point a browser tab to `http://localhost:3000/dashboard/script/bigchaindb_dashboard.js`.  Login and password are `admin` by default.  If BigchainDB is running and processing transactions, you should see analytics—if not, start BigchainDB as above, and refresh the page after a few seconds.

If you're not interested in monitoring, don't worry: BigchainDB will function just fine without any monitoring setup.

Feel free to modify the [custom Grafana dashboard](https://github.com/rhsimplex/grafana-bigchaindb-docker/blob/master/bigchaindb_dashboard.js) to your liking!