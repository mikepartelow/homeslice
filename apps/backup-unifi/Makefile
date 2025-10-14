SHELL := /bin/bash
CURRENCY := $(shell [[ ../make.mk -nt ./.make ]] && cp -v ../make.mk ./.make.mk 1>&2)

include ./.make.mk

test:
	echo FIXME

# FIXME: share with pulumi
lint:
	ruff check

fmt:
	ruff check --fix

VENV := ./.venv
venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --no-deps -r requirements.txt

lint: copy-libs

build: copy-libs

copy-libs:
	cp -v ../pylib/git.py lib/git.py
	cp -v ../pylib/github_backup.py lib/github_backup.py
