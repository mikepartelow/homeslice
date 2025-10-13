SHELL := /bin/bash
CURRENCY := $(shell [[ ../make.mk -nt ./.make ]] && cp -v ../make.mk ./.make.mk 1>&2)

include ./.make.mk


BACKUP_REPO_CLONE_DIR=/tmp/tidal_backuo_repo
CONFIG_PATH=../../pulumi/homeslice_secrets/gosonos-config.yaml
update-config: local
	rm -rf $(BACKUP_REPO_CLONE_DIR)
	git clone ${BACKUP_REPO_URL} $(BACKUP_REPO_CLONE_DIR)
	env CONFIG_PATH=$(CONFIG_PATH) \
		./gosonos update-config \
		--playlist-id mega-playlist \
		--output $(CONFIG_PATH).1 \
		--tidal-backup $(BACKUP_REPO_CLONE_DIR)/mega_playlist.json
	mv $(CONFIG_PATH) $(CONFIG_PATH).backup
	mv $(CONFIG_PATH).1 $(CONFIG_PATH)
