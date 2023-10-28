"""Resources for the homeslice/backup-todoist app."""

from pathlib import Path
import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
from homeslice_secrets import backup_todoist as BACKUP_TODOIST_SECRETS

NAME = "backup-todoist"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/backup-todoist app"""

    image = config["image"]
    private_key_path = config["private_key_path"]
    author_name = config["author_name"]
    author_email = config["author_email"]
    schedule = config["schedule"]

    ssh_name = NAME + "-ssh"

    known_hosts_name = NAME + "-known-hosts"
    known_hosts_path = config["known_hosts_path"]
    known_hosts = config["known_hosts"]

    homeslice.configmap(
        NAME,
        {
            "TODOIST_BACKUP_PRIVATE_KEY_PATH": private_key_path,
            "TODOIST_BACKUP_AUTHOR_NAME": author_name,
            "TODOIST_BACKUP_AUTHOR_EMAIL": author_email,
            "SSH_KNOWN_HOSTS": str(known_hosts_path),
        },
    )

    homeslice.configmap(
        known_hosts_name,
        {
            str(Path(known_hosts_path).name): known_hosts,
        },
    )

    kubernetes.core.v1.Secret(
        NAME,
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
            mount_path=str(Path(private_key_path).parent),
            read_only=True,
        ),
        kubernetes.core.v1.VolumeMountArgs(
            name=known_hosts_name,
            mount_path=str(Path(known_hosts_path).parent),
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
                name=known_hosts_name,
                default_mode=0o444,
            ),
        ),
    ]

    env_from = [
        homeslice.env_from_configmap(NAME),
        homeslice.env_from_secret(NAME),
    ]

    homeslice.cronjob(
        NAME,
        image,
        schedule,
        env_from=env_from,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )
