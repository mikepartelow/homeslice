.PHONY: venv venv-lint lint fmt
all: lint

VENV := .venv
venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

# FIXME: share with chime
VENV_LINT := ./.venv.lint
venv-lint:
	python3 -m venv $(VENV_LINT)
	$(VENV_LINT)/bin/pip install --no-deps -r requirements-lint.txt -r requirements.txt

lint: venv-lint
	$(VENV_LINT)/bin/black --exclude '.venv.*' --check .
	$(VENV_LINT)/bin/pylint --ignore-paths=.venv,.venv.lint "**/*.py"

fmt: venv-lint
	$(VENV_LINT)/bin/black --exclude '.venv.*' .
