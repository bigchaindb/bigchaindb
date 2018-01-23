from network_driver.network import Network


def test_peers_connected():
    n = Network(2)
    n.ensure_started()

    assert n.nodes[0].get_peers() == []
    assert n.nodes[1].get_peers() == []

    n.ensure_connected()

    assert len(n.nodes[0].get_peers()) == 1
    assert len(n.nodes[1].get_peers()) == 1

    n.stop()
