if curl -f http://bigchaindb:3333 && curl -f http://tendermint:26657/abci_query; then
  exit 0  # Both requests were successful
else
  exit 1  # At least one request failed
fi