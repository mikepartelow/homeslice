SHELL := /bin/bash
CURRENCY := $(shell [[ ../make.mk -nt ./.make ]] && cp -v ../make.mk ./.make.mk 1>&2)

override --docker-run-env += -e LOCATION=${LOCATION}
include ./.make.mk

test:
	echo FIXME

# FIXME: share with pulumi
VENV_LINT := ./venv.lint
venv-lint:
	python3 -m venv $(VENV_LINT)
	$(VENV_LINT)/bin/pip install --no-deps -r requirements-lint.txt -r requirements.txt

lint: venv-lint
	$(VENV_LINT)/bin/black --exclude '.venv.*' --check .
	$(VENV_LINT)/bin/pylint --ignore-paths=venv,venv.lint "**/*.py"

fmt: venv-lint
	$(VENV_LINT)/bin/black --exclude '.venv.*' .
