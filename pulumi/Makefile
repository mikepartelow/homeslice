.PHONY: venv venv-lint lint fmt
all: lint

VENV := .venv
venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

# FIXME: refactor to a common Python lint/fmt
lint:
	ruff check

fmt:
	ruff check --fix
