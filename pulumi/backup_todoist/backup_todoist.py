"""Resources for the homeslice/backup-todoist app."""

from pathlib import Path
import pulumi_kubernetes as kubernetes
import homeslice_config
import homeslice
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    backup_todoist as BACKUP_TODOIST_SECRETS,
)

NAME = "backup-todoist"


def app(config: homeslice_config.BackupTodoistConfig) -> None:
    """define resources for the homeslice/backup-todoist app"""

    image = config.image
    schedule = config.schedule

    config.git_clone_url = BACKUP_TODOIST_SECRETS.TODOIST_BACKUP_GIT_CLONE_URL
    btg = homeslice.BackupToGithub(NAME, config)

    homeslice.configmap(
        NAME,
        btg.configmap_items,
    )

    kubernetes.core.v1.Secret(
        NAME,  # pylint: disable=R0801
        metadata=homeslice.metadata(NAME),
        type="Opaque",
        string_data=btg.secret_items | {
            "TODOIST_TOKEN": BACKUP_TODOIST_SECRETS.TODOIST_TOKEN,
        },
    )

    btg.ssh_secret

    # pylint: disable=R0801
    homeslice.cronjob(
        NAME,
        image,
        schedule,
        env_from=btg.env_from,
        volumes=btg.volumes,
        volume_mounts=btg.volume_mounts,
    )
