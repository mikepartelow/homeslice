FLYTE_IMAGE_REGISTRY := registry.localdomain:32000
FLYTE_K8S_CONTEXT ?= ${FLYTE_K8S_CONTEXT}
FLYTE_PROJECT ?= remedy-tidal
PLAYLIST_ID := 8427c6cc-12cf-43c5-84ce-77fbc095e455
NEW_PLAYLIST_NAME := flyte-remedied

make fmt:
	@ruff check --fix src
	@ruff format src

lint:
	@ruff check src
	@uv run mypy src

test:
	@uv run pytest --tb=short -v
	@uv run coverage run -m pytest
	@uv run coverage report -m

SECRET_GROUP := tidal-creds
SECRET_KEY := json
SECRET_PATH := ../backup-tidal/tidal-creds.json

secret:
	kubectl --context $(FLYTE_K8S_CONTEXT) \
		create secret -n $(FLYTE_PROJECT)-development \
		generic \
		$(SECRET_GROUP) \
		--from-file=$(SECRET_KEY)=$(SECRET_PATH)

PYFLYTE_RUN_ARGS=--project $(FLYTE_PROJECT) \
	src/workflows/remedy_tidal.py remedy_tidal_wf \
	--playlist_id="$(PLAYLIST_ID)" \
	--new_playlist_name="$(NEW_PLAYLIST_NAME)" \
	--path_to_creds="$(TIDAL_CREDS_PATH)"

sandbox-rebuild-run-remote: FLYTE_FORCE_PUSH_IMAGE_SPEC := True
sandbox-rebuild-run-remote: sandbox-run-remote

create-project:
	flytectl create project \
      		--id "$(FLYTE_PROJECT)" \
      		--labels "project=$(FLYTE_PROJECT)" \
      		--description "$(FLYTE_PROJECT)" \
      		--name "$(FLYTE_PROJECT)"

sandbox-run-local: TIDAL_CREDS_PATH := ../backup-tidal/tidal-creds.json
sandbox-run-local:
	FLYTE_IMAGE_REGISTRY=$(FLYTE_IMAGE_REGISTRY) \
		uv run pyflyte run \
		$(PYFLYTE_RUN_ARGS)

run-remote: TIDAL_CREDS_PATH := /etc/flyte/secrets/tidal-creds/json
run-remote:
	FLYTE_FORCE_PUSH_IMAGE_SPEC=$(FLYTE_FORCE_PUSH_IMAGE_SPEC) \
	FLYTE_IMAGE_REGISTRY=$(FLYTE_IMAGE_REGISTRY) \
		uv run pyflyte run --remote \
		$(PYFLYTE_RUN_ARGS)

run: TIDAL_CREDS_PATH := ../backup-tidal/tidal-creds.json
run:
	FLYTE_IMAGE_REGISTRY=$(FLYTE_IMAGE_REGISTRY) \
		PYTHONPATH=src uv run ./src/workflows/remedy_tidal.py $(PLAYLIST_ID) $(NEW_PLAYLIST_NAME) $(TIDAL_CREDS_PATH)
