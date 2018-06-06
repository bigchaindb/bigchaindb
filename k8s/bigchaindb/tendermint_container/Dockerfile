FROM tendermint/tendermint:0.19.7
LABEL maintainer "dev@bigchaindb.com"
WORKDIR /
USER root
RUN apk --update add bash
COPY genesis.json.template /etc/tendermint/genesis.json
COPY tendermint_entrypoint.bash /
VOLUME /tendermint /tendermint_node_data
EXPOSE 46656 46657
ENTRYPOINT ["/tendermint_entrypoint.bash"]
