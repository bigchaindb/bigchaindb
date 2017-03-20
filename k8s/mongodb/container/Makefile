# Targets:
# 	all: Cleans, formats src files, builds the code, builds the docker image
# 	clean:  Removes the binary and docker image
#	format: Formats the src files
# 	build:  Builds the code
#	docker: Builds the code and docker image
#	push:   Push the docker image to Docker hub

GOCMD=go
GOVET=$(GOCMD) tool vet
GOINSTALL=$(GOCMD) install
GOFMT=gofmt -s -w

DOCKER_IMAGE_NAME?=bigchaindb/mongodb
DOCKER_IMAGE_TAG?=latest

PWD=$(shell pwd)
BINARY_PATH=$(PWD)/mongod_entrypoint/
BINARY_NAME=mongod_entrypoint
MAIN_FILE = $(BINARY_PATH)/mongod_entrypoint.go
SRC_FILES = $(BINARY_PATH)/mongod_entrypoint.go

.PHONY: all

all: clean build docker

clean:
	@echo "removing any pre-built binary";
	-@rm $(BINARY_PATH)/$(BINARY_NAME);
	@echo "remove any pre-built docker image";
	-@docker rmi $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG);

format:
	$(GOFMT) $(SRC_FILES)

build: format
	$(shell cd $(BINARY_PATH) && \
		export GOPATH="$(BINARY_PATH)" && \
		export GOBIN="$(BINARY_PATH)" && \
		CGO_ENABLED=0 GOOS=linux $(GOINSTALL) -ldflags "-s" -a -installsuffix cgo $(MAIN_FILE))

docker: build
	docker build \
		-t $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) .;

vet:
	$(GOVET) .

push:
	docker push \
		$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG);
