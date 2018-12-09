# Toolbox container for debugging
# Run as:
# docker run -it --rm --entrypoint sh bigchaindb/toolbox
# kubectl run -it toolbox --image bigchaindb/toolbox --restart=Never --rm

FROM alpine:3.5
LABEL maintainer "devs@bigchaindb.com"
WORKDIR /
RUN apk add --no-cache --update curl bind-tools python3-dev g++ \
        libffi-dev make vim git nodejs openssl-dev \
    && pip3 install ipython \
    && git clone https://github.com/bigchaindb/bigchaindb-driver \
    && cd bigchaindb-driver \
    && pip3 install -e . \
    && npm install -g wsc
ENTRYPOINT ["/bin/sh"]
