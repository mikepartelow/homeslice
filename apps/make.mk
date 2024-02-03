DEFAULT_REGISTRY := registry.localdomain:32000

PROJECT := $(notdir $(patsubst %/,%,$(dir $(abspath $(firstword $(MAKEFILE_LIST))))))
REGISTRY := $(if ${REGISTRY},${REGISTRY},$(DEFAULT_REGISTRY))
VERSION := $(if ${VERSION},${VERSION},$(shell date +'%Y%m%d_%H%M%S'))
IMAGE = $(REGISTRY)/$(PROJECT)

--docker-run-env :=
--docker-build-platform := --platform=linux/amd64
--docker-run-ports := -p 8000:8000
--docker-run-mounts := -v`pwd`:/app

--dev-args :=
--build-args := ${--docker-build-platform}
--run-args := ${--docker-run-ports} ${--docker-run-mounts} ${--docker-run-env}
--local-args :=
--shell-args := ${--docker-run-ports} ${--docker-run-mounts} ${--docker-run-env}

.PHONY: fmt lint info dev shell build run push local
all: build

info:
	echo "Project: ${PROJECT}"
	echo "Registry: ${REGISTRY}"
	echo "Version: ${VERSION}"
	echo "Image: ${IMAGE}"
	echo "MAKEFILE_LIST: ${MAKEFILE_LIST}"

fmt:
	go fmt ./...

lint:
	golangci-lint run

dev:
	docker build ${--dev-args} -t $(PROJECT)-dev --target dev .

shell: dev
	docker run --rm --entrypoint '' -ti ${--shell-args} $(PROJECT)-dev /bin/bash

test:
	go test -race -cover ./...

build: test
	docker build ${--build-args} -t $(IMAGE):$(VERSION) --target prod .

run: build
	docker run --rm -t ${--run-args} $(IMAGE):$(VERSION)

push: build
	docker push $(IMAGE):$(VERSION)

local:
	CGO_ENABLED=0 go build ${--local-args} -o . ./cmd/...
