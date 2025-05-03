FLYTE_IMAGE_REGISTRY := registry.localdomain:32000
FLYTE_PROJECT := remedy-tidal
PLAYLIST_ID := 8427c6cc-12cf-43c5-84ce-77fbc095e455
TIDAL_CREDS_PATH := ../backup-tidal/tidal-creds.json

make fmt:
	@ruff check --fix

lint:
	@ruff check
	@uv run mypy .

PYFLYTE_RUN_ARGS=--project $(FLYTE_PROJECT) \
	src/workflows/remedy_tidal.py remedy_tidal_wf \
	--playlist_id="$(PLAYLIST_ID)" \
	--path_to_creds="$(TIDAL_CREDS_PATH)"

sandbox-create-project:
	flytectl create project \
      		--id "$(FLYTE_PROJECT)" \
      		--labels "project=$(FLYTE_PROJECT)" \
      		--description "$(FLYTE_PROJECT)" \
      		--name "$(FLYTE_PROJECT)"

sandbox-run-local:
	FLYTE_IMAGE_REGISTRY=$(FLYTE_IMAGE_REGISTRY) \
		uv run pyflyte run \
		$(PYFLYTE_RUN_ARGS)

sandbox-run-remote:
	FLYTE_IMAGE_REGISTRY=$(FLYTE_IMAGE_REGISTRY) \
		uv run pyflyte run --remote \
		$(PYFLYTE_RUN_ARGS)

run:
	FLYTE_IMAGE_REGISTRY=$(FLYTE_IMAGE_REGISTRY) \
		PATH_TO_CREDS=$(TIDAL_CREDS_PATH) \
		PYTHONPATH=src uv run ./src/workflows/remedy_tidal.py $(PLAYLIST_ID) $(TIDAL_CREDS_PATH)
