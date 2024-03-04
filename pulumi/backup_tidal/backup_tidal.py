"""Resources for the homeslice/backup-todoist app."""

from pathlib import Path
import pulumi_kubernetes as kubernetes
import pulumi
import homeslice
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    backup_tidal as BACKUP_TIDAL_SECRETS,
)

NAME = "backup-tidal"
CONFIG_PATH = "/var/run/secrets/backup-tidal.json"
TIDAL_CREDS_PATH = "/var/run/secrets/tidal-creds.json"
KNOWN_HOSTS_PATH = "/var/run/known_hosts/known_hosts"
PRIVATE_KEY_PATH = "/var/run/ssh-privatekey/ssh-privatekey"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/backup-tidal app"""

    git_author = config["git_author"]
    image = config["image"]
    known_hosts = config["known_hosts"]
    schedule = config["schedule"]

    known_hosts_name = NAME + "-known-hosts"
    ssh_name = NAME + "-ssh"

    # FIXME: refactor the github boilerplate here and todoist

    homeslice.configmap(
        NAME,
        {
            "BACKUP_REPO": BACKUP_TIDAL_SECRETS.BACKUP_REPO,
            "CLONE_PATH": "/tmp",
            "GIT_AUTHOR": git_author,
            "GIT_SSH_COMMAND": f"ssh -i {PRIVATE_KEY_PATH} -o UserKnownHostsFile={KNOWN_HOSTS_PATH}",
            "OUTPUT_PATH": "/tmp",
            "PATH_TO_CONFIG": CONFIG_PATH,
            "PLAYLIST_PATH": "/tmp",
            "PATH_TO_CREDS": TIDAL_CREDS_PATH,
            "PRIVATE_KEY_PATH": PRIVATE_KEY_PATH,
            "SSH_KNOWN_HOSTS": str(KNOWN_HOSTS_PATH),
            str(Path(KNOWN_HOSTS_PATH).name): known_hosts,
        },
    )

    kubernetes.core.v1.Secret(
        NAME,
        metadata=homeslice.metadata(NAME),
        type="Opaque",
        string_data={
            Path(TIDAL_CREDS_PATH).name: BACKUP_TIDAL_SECRETS.TIDAL_CREDS_JSON,
            Path(CONFIG_PATH).name: BACKUP_TIDAL_SECRETS.CONFIG_JSON,
        },
    )

    kubernetes.core.v1.Secret(
        ssh_name,
        metadata=homeslice.metadata(ssh_name),
        type="kubernetes.io/ssh-auth",
        string_data={
            "ssh-privatekey": BACKUP_TIDAL_SECRETS.SSH_PRIVATE_KEY,
        },
    )

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=NAME,
            mount_path=str(Path(TIDAL_CREDS_PATH).parent),
            read_only=True,
        ),
        kubernetes.core.v1.VolumeMountArgs(
            name=known_hosts_name,
            mount_path=str(Path(KNOWN_HOSTS_PATH).parent),
            read_only=True,
        ),
        kubernetes.core.v1.VolumeMountArgs(
            name=ssh_name,
            mount_path=str(Path(PRIVATE_KEY_PATH).parent),
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
        kubernetes.core.v1.VolumeArgs(
            name=known_hosts_name,
            config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                name=NAME,
                default_mode=0o444,
                items=[
                    {
                        "key": str(Path(KNOWN_HOSTS_PATH).name),
                        "path": str(Path(KNOWN_HOSTS_PATH).name),
                    }
                ],
            ),
        ),
        kubernetes.core.v1.VolumeArgs(
            name=ssh_name,
            secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                secret_name=ssh_name,
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
        command=["/bin/bash", "-c", "--"],
        args=["while true; do sleep 30; done;"],
        env_from=env_from,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )
