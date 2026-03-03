DEFAULT_REGISTRY := registry.localdomain:32000

PROJECT := $(notdir $(patsubst %/,%,$(dir $(abspath $(firstword $(MAKEFILE_LIST))))))
REGISTRY := $(if $(REGISTRY),$(REGISTRY),$(DEFAULT_REGISTRY))
VERSION := $(if $(VERSION),$(VERSION),$(shell date +'%Y%m%d_%H%M%S'))
IMAGE = $(REGISTRY)/$(PROJECT)
DOCKER_PLATFORMS ?= linux/amd64,linux/arm64
DOCKER_BUILDX_BUILDER ?= homeslice-multiarch

--docker-run-env :=
--docker-build-platform := --platform=linux/amd64
--docker-run-ports := -p 8000:8000
--docker-run-mounts := -v`pwd`:/app

--dev-args :=
--build-args := ${--docker-build-platform}
--run-args := ${--docker-run-ports} ${--docker-run-mounts} ${--docker-run-env}
--local-args :=
--shell-args := ${--docker-run-ports} ${--docker-run-mounts} ${--docker-run-env}

.PHONY: fmt lint info dev shell build run push local buildx-ensure
all: build

info:
	@echo "Project: ${PROJECT}"
	@echo "Registry: ${REGISTRY}"
	@echo "Version: ${VERSION}"
	@echo "Image: ${IMAGE}"
	@echo "MAKEFILE_LIST: ${MAKEFILE_LIST}"

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

buildx-ensure:
	docker buildx inspect $(DOCKER_BUILDX_BUILDER) >/dev/null 2>&1 || docker buildx create --name $(DOCKER_BUILDX_BUILDER) --use
	docker buildx use $(DOCKER_BUILDX_BUILDER)
	docker buildx inspect --bootstrap >/dev/null

build: test
	docker build ${--build-args} -t $(IMAGE):$(VERSION) --target prod .

run: build
	docker run --rm -t ${--run-args} $(IMAGE):$(VERSION)

push: test buildx-ensure
	docker buildx build --platform $(DOCKER_PLATFORMS) -t $(IMAGE):$(VERSION) --target prod --push .

local:
	CGO_ENABLED=0 go build ${--local-args} -o . ./cmd/...
