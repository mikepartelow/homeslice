.PHONY: lint fmt
all: lint

bump:
	rm -f bump-cache.yaml
	uv run --no-project ./bump.py

# FIXME: refactor to a common Python lint/fmt
make fmt:
	@ruff check --fix
	@ruff format

lint:
	@ruff check
	@uv run mypy .
