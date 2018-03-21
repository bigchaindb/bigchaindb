FROM tendermint/tendermint:0.12
LABEL maintainer "dev@bigchaindb.com"
WORKDIR /
COPY genesis.json.template /etc/tendermint/genesis.json
COPY tendermint_entrypoint.bash /
VOLUME /tendermint /tendermint_node_data
EXPOSE 46656 46657
ENTRYPOINT ["/tendermint_entrypoint.bash"]
