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
lint:
	ruff check

fmt:
	ruff check --fix

VENV := ./.venv
venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --no-deps -r requirements.txt

login: dev
	docker run --rm --entrypoint '' -ti ${--shell-args} $(PROJECT)-dev ./login_tidal.py

backup: dev
	docker run --rm --entrypoint '' -v`pwd`/tmp:/tmp -ti ${--shell-args} $(PROJECT)-dev ./backup_tidal.py

lint: copy-libs

build: copy-libs

copy-libs:
	cp -v ../pylib/git.py lib/git.py
	cp -v ../pylib/github_backup.py lib/github_backup.py

UNAVAILABLE_JSON_PATH := tmp/unavailable.json
find-unavailable:
	jq '[.[] | select(.available == false)]' tmp/mega_playlist.json > $(UNAVAILABLE_JSON_PATH)

remedy-unavailables: dev
	docker run --rm --entrypoint '' -v`pwd`/tmp:/tmp -ti ${--shell-args} $(PROJECT)-dev ./remedy_unavailables.py /$(UNAVAILABLE_JSON_PATH) "remedied jamboree"
