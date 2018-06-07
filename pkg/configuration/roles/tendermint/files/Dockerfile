ARG tm_version=0.19.9
FROM tendermint/tendermint:${tm_version}
LABEL maintainer "dev@bigchaindb.com"
WORKDIR /
USER root
RUN apk --update add bash
ENTRYPOINT ["/usr/bin/tendermint"]
