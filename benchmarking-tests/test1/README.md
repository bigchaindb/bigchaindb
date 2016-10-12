# Transactions per second

Measure how many blocks per second are created on the _bigchain_ with a pre filled backlog.

1. Deploy an aws cluster https://docs.bigchaindb.com/projects/server/en/latest/clusters-feds/aws-testing-cluster.html
2. Make a symbolic link to hostlist.py: `ln -s ../deploy-cluster-aws/hostlist.py .`
3. Make a symbolic link to bigchaindb.pem:
```bash
mkdir pem
cd pem
ln -s ../deploy-cluster-aws/pem/bigchaindb.pem .
```

Then:

```bash
fab put_benchmark_utils
fab set_statsd_host:<hostname of the statsd server>
fab prepare_backlog:<num txs per node> # wait for process to finish
fab start_bigchaindb
```