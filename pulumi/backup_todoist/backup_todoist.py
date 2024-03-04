"""Resources for the homeslice/backup-todoist app."""

from pathlib import Path
import pulumi_kubernetes as kubernetes
import pulumi
import homeslice
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    backup_todoist as BACKUP_TODOIST_SECRETS,
)

NAME = "backup-todoist"
KNOWN_HOSTS_PATH = "/var/run/known_hosts/known_hosts"
PRIVATE_KEY_PATH = "/var/run/ssh-privatekey/ssh-privatekey"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/backup-todoist app"""

    author_name = config["author_name"]
    author_email = config["author_email"]
    image = config["image"]
    known_hosts = config["known_hosts"]
    schedule = config["schedule"]

    known_hosts_name = NAME + "-known-hosts"
    ssh_name = NAME + "-ssh"

    homeslice.configmap(
        NAME,
        {
            "TODOIST_BACKUP_PRIVATE_KEY_PATH": PRIVATE_KEY_PATH,
            "TODOIST_BACKUP_AUTHOR_NAME": author_name,
            "TODOIST_BACKUP_AUTHOR_EMAIL": author_email,
            "SSH_KNOWN_HOSTS": str(KNOWN_HOSTS_PATH),
            str(Path(KNOWN_HOSTS_PATH).name): known_hosts,
        },
    )

    kubernetes.core.v1.Secret(
        NAME,  # pylint: disable=R0801
        metadata=homeslice.metadata(NAME),
        type="Opaque",
        string_data={
            "TODOIST_BACKUP_GIT_CLONE_URL": BACKUP_TODOIST_SECRETS.TODOIST_BACKUP_GIT_CLONE_URL,
            "TODOIST_BACKUP_TODOIST_TOKEN": BACKUP_TODOIST_SECRETS.TODOIST_BACKUP_TODOIST_TOKEN,
        },
    )

    kubernetes.core.v1.Secret(
        ssh_name,
        metadata=homeslice.metadata(ssh_name),
        type="kubernetes.io/ssh-auth",
        string_data={
            "ssh-privatekey": BACKUP_TODOIST_SECRETS.SSH_PRIVATE_KEY,
        },
    )

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=ssh_name,
            mount_path=str(Path(PRIVATE_KEY_PATH).parent),
            read_only=True,
        ),
        kubernetes.core.v1.VolumeMountArgs(
            name=known_hosts_name,
            mount_path=str(Path(KNOWN_HOSTS_PATH).parent),
            read_only=True,
        ),
    ]

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name=ssh_name,
            secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                secret_name=ssh_name,
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
    ]

    env_from = [
        homeslice.env_from_configmap(NAME),
        homeslice.env_from_secret(NAME),
    ]

    # pylint: disable=R0801
    homeslice.cronjob(
        NAME,
        image,
        schedule,
        env_from=env_from,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )
