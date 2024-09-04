"""Resources for the homeslice/backup-todoist app."""

from pathlib import Path
import pulumi_kubernetes as kubernetes
import homeslice_config
import homeslice
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    backup_tidal as BACKUP_TIDAL_SECRETS,
)

NAME = "backup-tidal"
CONFIG_PATH = "/var/run/secrets/backup-tidal.json"
TIDAL_CREDS_PATH = "/var/run/secrets/tidal-creds.json"

SSH_FILES_PATH = "/ssh"
KNOWN_HOSTS_PATH = SSH_FILES_PATH + "/known_hosts"
PRIVATE_KEY_PATH = SSH_FILES_PATH + "/id_rsa"


GIT_SSH_COMMAND = f"ssh -i {PRIVATE_KEY_PATH} -o UserKnownHostsFile={KNOWN_HOSTS_PATH}"


def app(config: homeslice_config.BackupTidalConfig) -> None:
    """define resources for the homeslice/backup-tidal app"""

    image = config.image
    schedule = config.schedule

    config.git_clone_url = BACKUP_TIDAL_SECRETS.GIT_CLONE_URL
    config.ssh_private_key = BACKUP_TIDAL_SECRETS.SSH_PRIVATE_KEY
    btg = homeslice.BackupToGithub(NAME, config)

    homeslice.configmap(
        NAME,
        btg.configmap_items
        | {
            "PATH_TO_CONFIG": CONFIG_PATH,
            "PATH_TO_CREDS": TIDAL_CREDS_PATH,
        },
    )

    btg.ssh_secret

    kubernetes.core.v1.Secret(
        NAME,
        metadata=homeslice.metadata(NAME),
        type="Opaque",
        string_data=btg.secret_items
        | {
            Path(CONFIG_PATH).name: BACKUP_TIDAL_SECRETS.CONFIG_JSON,
            Path(TIDAL_CREDS_PATH).name: BACKUP_TIDAL_SECRETS.TIDAL_CREDS_JSON,
        },
    )

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=NAME,
            mount_path=str(Path(TIDAL_CREDS_PATH).parent),
            read_only=True,
        )
    ]

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name=NAME,
            secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                secret_name=NAME,
                default_mode=0o444,
            ),
        ),
    ]

    env_from = [homeslice.env_from_configmap(NAME)]

    homeslice.cronjob(
        NAME,
        image,
        schedule,
        env_from=btg.env_from + env_from,
        volumes=btg.volumes + volumes,
        volume_mounts=btg.volume_mounts + volume_mounts,
    )
