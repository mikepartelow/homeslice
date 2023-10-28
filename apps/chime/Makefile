SHELL := /bin/bash
CURRENCY := $(shell [[ ../make.mk -nt ./.make ]] && cp -v ../make.mk ./.make.mk 1>&2)

override --docker-run-env += -e LOCATION=${LOCATION}
include ./.make.mk

test:
	echo FIXME

LINTER_IMAGE := homeslice-chime-linter

linter:
	docker build -t $(LINTER_IMAGE) -f Dockerfile-lint .

ifeq ($(CI),TRUE)
lint:
	black --check . && pylint  --ignore-paths=venv "**/*.py"
else
lint: linter
	docker run --rm -v`pwd`:/app -ti $(LINTER_IMAGE) bash -c 'black --check . && pylint  --ignore-paths=venv "**/*.py"'

fmt: linter
	docker run --rm -v`pwd`:/app -ti $(LINTER_IMAGE) bash -c 'black .'
endif
