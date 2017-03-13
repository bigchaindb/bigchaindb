# Toolbox container for debugging
# Run as:
# docker run -it --rm --entrypoint sh krish7919/toolbox
# kubectl run -it toolbox --image krish7919/toolbox --restart=Never --rm

FROM alpine:3.5
MAINTAINER github.com/krish7919
WORKDIR /

RUN apk add --no-cache curl bind-tools

ENTRYPOINT ["/bin/sh"]
