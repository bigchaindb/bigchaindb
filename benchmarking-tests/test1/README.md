# Transactions per second

Measure how many blocks per second are created on the _bigchain_ with a pre filled backlog.

1. Deploy an aws cluster http://bigchaindb.readthedocs.io/en/latest/deploy-on-aws.html
2. Copy `deploy-cluster-aws/hostlist.py` to `benchmarking-tests`

```bash
fab put_benchmark_utils
fab set_statsd_host:<hostname of the statsd server>
fab prepare_backlog:<num txs per node> # wait for process to finish
fab start_bigchaindb
```