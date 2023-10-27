.PHONY: linter lint
all: lint

LINTER_IMAGE := homeslice-pulumi-linter

linter:
	docker build -t $(LINTER_IMAGE) -f Dockerfile-lint .

lint: linter
	docker run --rm -v`pwd`:/app -ti $(LINTER_IMAGE) bash -c 'black --check . && pylint  --ignore-paths=venv "**/*.py"'

fmt: linter
	docker run --rm -v`pwd`:/app -ti $(LINTER_IMAGE) bash -c 'black .'
