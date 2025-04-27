.PHONY: lint fmt
all: lint

bump:
	rm -f bump-cache.yaml
	uv run --no-project ./bump.py

# FIXME: refactor to a common Python lint/fmt
lint:
	ruff check

fmt:
	ruff check --fix
