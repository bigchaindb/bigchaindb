from platform import node


def test_monitor_class_init_defaults():
    import bigchaindb
    from bigchaindb.monitor import Monitor
    monitor = Monitor()
    assert monitor
    assert len(monitor._addr) == 2
    # TODO get value from config
    # assert monitor._addr[0] == bigchaindb.config['statsd']['host']
    assert monitor._addr[0] == '127.0.0.1'
    assert monitor._addr[1] == bigchaindb.config['statsd']['port']
    assert monitor._prefix == node() + '.'
