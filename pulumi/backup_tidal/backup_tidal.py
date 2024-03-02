"""Resources for the homeslice/backup-todoist app."""

from pathlib import Path
import pulumi_kubernetes as kubernetes
import pulumi
import homeslice
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    backup_tidal as BACKUP_TIDAL_SECRETS,
)

NAME = "backup-tidal"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/backup-tidal app"""

    image = config["image"]
    schedule = config["schedule"]
    tidal_creds_path = config["tidal_creds_path"]

    tidal_creds_name = NAME + "-creds"

    # FIXME: refactor the github boilerplate here and todoist

    kubernetes.core.v1.Secret(
        tidal_creds_name,
        metadata=homeslice.metadata(tidal_creds_name),
        type="Opaque",
        string_data={
            Path(tidal_creds_path).name: BACKUP_TIDAL_SECRETS.TIDAL_CREDS_JSON,
        },
    )

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=tidal_creds_name,
            mount_path=str(Path(tidal_creds_path).parent),
            read_only=True,
        ),
    ]

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name=tidal_creds_name,
            secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                secret_name=tidal_creds_name,
                default_mode=0o444,
            ),
        ),
    ]

    # homeslice.cronjob(
    #     NAME,
    #     image,
    #     schedule,
    #     env_from=env_from,
    #     volumes=volumes,
    #     volume_mounts=volume_mounts,
    # )

    homeslice.deployment(
        NAME,
        image,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )
