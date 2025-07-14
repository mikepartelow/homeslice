"""Resources for the homeslice/backup-todoist app."""

from pathlib import Path
import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
import homeslice_config
from homeslice_secrets import (  # pylint: disable=no-name-in-module  # type: ignore
    backup_tidal as BACKUP_TIDAL_SECRETS,
)

CONFIG_PATH = "/var/run/secrets/backup-tidal.json"
TIDAL_CREDS_PATH = "/var/run/secrets/tidal-creds.json"

SSH_FILES_PATH = "/ssh"
KNOWN_HOSTS_PATH = SSH_FILES_PATH + "/known_hosts"
PRIVATE_KEY_PATH = SSH_FILES_PATH + "/id_rsa"


GIT_SSH_COMMAND = f"ssh -i {PRIVATE_KEY_PATH} -o UserKnownHostsFile={KNOWN_HOSTS_PATH}"


class BackupTidal(pulumi.ComponentResource):
    """Backup Tidal app resources."""

    def __init__(self, name: str, config: homeslice_config.BackupTidalConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:backup_tidal:BackupTidal", name, {}, opts)

        image = config.image
        schedule = config.schedule

        config.git_clone_url = BACKUP_TIDAL_SECRETS.GIT_CLONE_URL
        config.ssh_private_key = BACKUP_TIDAL_SECRETS.SSH_PRIVATE_KEY.encode() if BACKUP_TIDAL_SECRETS.SSH_PRIVATE_KEY else None
        btg = homeslice.BackupToGithub(name, config)

        self.configmap = homeslice.configmap(
            name,
            btg.configmap_items
            | {
                "PATH_TO_CONFIG": CONFIG_PATH,
                "PATH_TO_CREDS": TIDAL_CREDS_PATH,
            },
        )

        self.ssh_secret = btg.ssh_secret  # this line does a lot more than it appears to do!

        self.secret = kubernetes.core.v1.Secret(
            name,
            metadata=homeslice.metadata(name),
            type="Opaque",
            string_data=btg.secret_items
            | {
                Path(CONFIG_PATH).name: BACKUP_TIDAL_SECRETS.CONFIG_JSON,
                Path(TIDAL_CREDS_PATH).name: BACKUP_TIDAL_SECRETS.TIDAL_CREDS_JSON,
            },
        )

        volume_mounts = [
            kubernetes.core.v1.VolumeMountArgs(
                name=name,
                mount_path=str(Path(TIDAL_CREDS_PATH).parent),
                read_only=True,
            )
        ]

        volumes = [
            kubernetes.core.v1.VolumeArgs(
                name=name,
                secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                    secret_name=name,
                    default_mode=0o444,
                ),
            ),
        ]

        env_from = [homeslice.env_from_configmap(name)]

        self.cronjob = homeslice.cronjob(
            name,
            image,
            schedule,
            env_from=btg.env_from + env_from,
            volumes=btg.volumes + volumes,
            volume_mounts=btg.volume_mounts + volume_mounts,
        )

        self.register_outputs({})
