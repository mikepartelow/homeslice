SHELL := /bin/bash
CURRENCY := $(shell [[ ../make.mk -nt ./.make ]] && cp -v ../make.mk ./.make.mk 1>&2)

include ./.make.mk

test:
	echo FIXME

# FIXME: share with pulumi
lint:
	ruff check
	uvx mypy .

fmt:
	ruff check --fix
