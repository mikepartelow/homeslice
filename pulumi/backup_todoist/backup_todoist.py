"""Resources for the homeslice/backup-todoist app."""

import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
import homeslice_config
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    backup_todoist as BACKUP_TODOIST_SECRETS,
)


class BackupTodoist(pulumi.ComponentResource):
    """Backup Todoist app resources."""

    def __init__(self, name: str, config: homeslice_config.BackupTodoistConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:backup_todoist:BackupTodoist", name, {}, opts)

        image = config.image
        schedule = config.schedule

        config.git_clone_url = BACKUP_TODOIST_SECRETS.GIT_CLONE_URL
        config.ssh_private_key = BACKUP_TODOIST_SECRETS.SSH_PRIVATE_KEY.encode() if BACKUP_TODOIST_SECRETS.SSH_PRIVATE_KEY else None
        btg = homeslice.BackupToGithub(name, config)

        self.configmap = homeslice.configmap(
            name,
            btg.configmap_items,
        )

        self.ssh_secret = btg.ssh_secret  # this line does a lot more than it appears to do!

        self.secret = kubernetes.core.v1.Secret(
            name,  # pylint: disable=R0801
            metadata=homeslice.metadata(name),
            type="Opaque",
            string_data=btg.secret_items
            | {
                "TODOIST_TOKEN": BACKUP_TODOIST_SECRETS.TODOIST_TOKEN,
            },
        )

        # pylint: disable=R0801
        self.cronjob = homeslice.cronjob(
            name,
            image,
            schedule,
            env_from=btg.env_from,
            volumes=btg.volumes,
            volume_mounts=btg.volume_mounts,
        )

        self.register_outputs({})


def app(config: homeslice_config.BackupTodoistConfig) -> None:
    """Define resources for the homeslice/backup-todoist app.
    
    Creates a BackupTodoist ComponentResource with cronjob, configmap, and secrets
    for backing up Todoist data to GitHub.
    """
    BackupTodoist("backup-todoist", config)
