# Troubleshooting

## General Tips

- Check the BigchainDB, Tendermint and MongoDB logs.
  For help with that, see the page about [Logging and Log Rotation](../appendices/log-rotation).
- Try Googling the error message.

## Resolving Tendermint Connectivity Problems

To check which nodes your node is connected to (via Tendermint protocols), do:

```text
# if you don't have jq installed, then install it
sudo apt install jq
# then do
curl -s localhost:26657/net_info | jq ".result.peers[].node_info | {id, listen_addr, moniker}"
```

Note: Tendermint has other endpoints besides `/net_info`: see [the Tendermint RPC docs](https://tendermint.github.io/slate/?shell#introduction).

If you're running your network inside a [private network](https://en.wikipedia.org/wiki/Private_network), e.g. with IP addresses of the form 192.168.x.y, then you may have to change the following setting in `config.toml`:

```text
addr_book_strict = false
```

## Other Problems

See the [Tendermint tips in the vrde/notes repository](https://github.com/vrde/notes/tree/master/tendermint).

If you're stuck, maybe [file a new issue on GitHub](https://github.com/bigchaindb/bigchaindb/issues/new). If your problem occurs often enough, we'll write about it here.
