SHELL := /bin/bash
CURRENCY := $(shell [[ ../make.mk -nt ./.make ]] && cp -v ../make.mk ./.make.mk 1>&2)

override --docker-run-env += -e BACKUP_REPO='$(BACKUP_REPO)' \
							 -e CLONE_PATH=tmp \
							 -e GIT_AUTHOR='$(GIT_AUTHOR)' \
							 -e PATH_TO_CONFIG=/app/backup-tidal.json \
 							 -e PATH_TO_CREDS=/app/tidal-creds.json \
							 -e PLAYLIST_PATH=tmp \
							 --mount type=bind,source=$(realpath $(HOME))/.ssh,target=/root/.ssh,readonly


include ./.make.mk

test:
	echo FIXME

# FIXME: share with pulumi
VENV_LINT := ./venv.lint
venv-lint:
	python3 -m venv $(VENV_LINT)
	$(VENV_LINT)/bin/pip install --no-deps -r requirements-lint.txt -r requirements.txt

lint: venv-lint
	$(VENV_LINT)/bin/black --exclude 'venv.*' --check .
	$(VENV_LINT)/bin/pylint --ignore-paths=venv,venv.lint "**/*.py"

fmt: venv-lint
	$(VENV_LINT)/bin/black --exclude 'venv.*' .

VENV := ./venv
venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --no-deps -r requirements.txt

login: dev
	docker run --rm --entrypoint '' -ti ${--shell-args} $(PROJECT)-dev ./login-tidal.py

backup: dev
	docker run --rm --entrypoint '' -ti ${--shell-args} $(PROJECT)-dev ./backup-tidal.py
