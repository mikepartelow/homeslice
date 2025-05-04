FLYTE_IMAGE_REGISTRY := registry.localdomain:32000
FLYTE_PROJECT := remedy-tidal
PLAYLIST_ID := 8427c6cc-12cf-43c5-84ce-77fbc095e455

make fmt:
	@ruff check --fix
	@ ruff format

lint:
	@ruff check
	@uv run mypy .

SECRET_GROUP := tidal-creds
SECRET_KEY := json
SECRET_PATH := ../backup-tidal/tidal-creds.json

secret:
	kubectl --context flyte-sandbox \
		create secret -n $(FLYTE_PROJECT)-development \
		generic \
		$(SECRET_GROUP) \
		--from-file=$(SECRET_KEY)=$(SECRET_PATH)

PYFLYTE_RUN_ARGS=--project $(FLYTE_PROJECT) \
	src/workflows/remedy_tidal.py remedy_tidal_wf \
	--playlist_id="$(PLAYLIST_ID)" \
	--path_to_creds="$(TIDAL_CREDS_PATH)"

sandbox-rebuild-run-remote: FLYTE_FORCE_PUSH_IMAGE_SPEC := True
sandbox-rebuild-run-remote: sandbox-run-remote

sandbox-create-project:
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

sandbox-run-remote: TIDAL_CREDS_PATH := /etc/flyte/secrets/tidal-creds/json
sandbox-run-remote:
	FLYTE_FORCE_PUSH_IMAGE_SPEC=$(FLYTE_FORCE_PUSH_IMAGE_SPEC) \
	FLYTE_IMAGE_REGISTRY=$(FLYTE_IMAGE_REGISTRY) \
		uv run pyflyte run --remote \
		$(PYFLYTE_RUN_ARGS)

run:
	FLYTE_IMAGE_REGISTRY=$(FLYTE_IMAGE_REGISTRY) \
		PATH_TO_CREDS=$(TIDAL_CREDS_PATH) \
		PYTHONPATH=src uv run ./src/workflows/remedy_tidal.py $(PLAYLIST_ID) $(TIDAL_CREDS_PATH)
