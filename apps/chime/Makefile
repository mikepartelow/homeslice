SHELL := /bin/bash
CURRENCY := $(shell [[ ../make.mk -nt ./.make ]] && cp -v ../make.mk ./.make.mk 1>&2)

override --docker-run-env += -e LOCATION=${LOCATION}
include ./.make.mk

test:
	echo FIXME
