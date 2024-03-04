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

    config_path = config["config_path"]
    image = config["image"]
    output_path = config["backup_path"]
    schedule = config["schedule"]
    tidal_creds_path = config["tidal_creds_path"]

    # FIXME: refactor the github boilerplate here and todoist

    homeslice.configmap(
        NAME,
        {
            "OUTPUT_PATH": output_path,
            "PATH_TO_CONFIG": config_path,
            "PATH_TO_CREDS": tidal_creds_path,
        },
    )

    kubernetes.core.v1.Secret(
        NAME,
        metadata=homeslice.metadata(NAME),
        type="Opaque",
        string_data={
            Path(tidal_creds_path).name: BACKUP_TIDAL_SECRETS.TIDAL_CREDS_JSON,
            Path(config_path).name: BACKUP_TIDAL_SECRETS.CONFIG_JSON,
        },
    )

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=NAME,
            mount_path=str(Path(tidal_creds_path).parent),
            read_only=True,
        ),
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

    env_from = [ homeslice.env_from_configmap(NAME) ]

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
        env_from=env_from,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )
