ARG tm_version=0.22.8
FROM tendermint/tendermint:${tm_version}
LABEL maintainer "devs@bigchaindb.com"
WORKDIR /
USER root
RUN apk --update add bash
ENTRYPOINT ["/usr/bin/tendermint"]
