.PHONY: linter lint
all: lint

LINTER_IMAGE := homeslice-pulumi-linter

linter:
	docker build -t $(LINTER_IMAGE) -f Dockerfile-lint .

ifeq ($(CI),TRUE)
PROJECT := pulumi
VENV := /tmp/venv.$(PROJECT)
lint:
	python -m venv $(VENV)
	$(VENV)/bin/pip install --no-deps -r /tmp/requirements-lint.txt -r /tmp/requirements.txt
	$(VENV)/bin/black --check .
	$(VENV)/bin/pylint  --ignore-paths=venv "**/*.py"
else
lint: linter
	docker run --rm -v`pwd`:/app -ti $(LINTER_IMAGE) bash -c 'pylint --ignore-paths=venv,homeslice_secrets "**/*.py" && black --check .'

fmt: linter
	docker run --rm -v`pwd`:/app -ti $(LINTER_IMAGE) bash -c 'black .'
endif
