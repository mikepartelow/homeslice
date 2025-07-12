.PHONY: lint fmt test clean deploy bump
all: lint test

bump:
	rm -f bump-cache.yaml
	uv run --no-project ./bump.py

fmt:
	@ruff check --fix
	@ruff format

lint:
	@ruff check
	@uv run mypy . --ignore-missing-imports

test:
	@echo "Running tests..."
	# @uv run pytest tests/  # Uncomment when tests are implemented

clean:
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name ".mypy_cache" -delete
	@find . -type d -name ".ruff_cache" -delete

deploy: lint test
	@pulumi up --stack prod --yes

deploy-dry-run:
	@pulumi preview --stack prod

logs:
	@pulumi logs --stack prod --follow
