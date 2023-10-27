"""Resources for the homeslice/backup-todoist app."""

from pathlib import Path
import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
from homeslice_secrets import backup_todoist as BACKUP_TODOIST_SECRETS

NAME = "backup-todoist"


def app(namespace: str, config: pulumi.Config) -> None:
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

    metadata = homeslice.metadata(NAME, namespace)

    kubernetes.core.v1.ConfigMap(
        NAME,
        metadata=metadata,
        data=dict(
            TODOIST_BACKUP_PRIVATE_KEY_PATH=private_key_path,
            TODOIST_BACKUP_AUTHOR_NAME=author_name,
            TODOIST_BACKUP_AUTHOR_EMAIL=author_email,
            SSH_KNOWN_HOSTS=str(known_hosts_path),
        ),
    )

    kubernetes.core.v1.ConfigMap(
        known_hosts_name,
        metadata=homeslice.metadata(known_hosts_name, namespace),
        data={
            str(Path(known_hosts_path).name): known_hosts,
        },
    )

    kubernetes.core.v1.Secret(
        NAME,
        metadata=metadata,
        type="Opaque",
        string_data=dict(
            TODOIST_BACKUP_GIT_CLONE_URL=BACKUP_TODOIST_SECRETS.TODOIST_BACKUP_GIT_CLONE_URL,
            TODOIST_BACKUP_TODOIST_TOKEN=BACKUP_TODOIST_SECRETS.TODOIST_BACKUP_TODOIST_TOKEN,
        ),
    )

    kubernetes.core.v1.Secret(
        ssh_name,
        metadata=homeslice.metadata(ssh_name, namespace),
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
        kubernetes.core.v1.EnvFromSourceArgs(
            config_map_ref=kubernetes.core.v1.ConfigMapEnvSourceArgs(
                name=NAME,
            )
        ),
        kubernetes.core.v1.EnvFromSourceArgs(
            secret_ref=kubernetes.core.v1.SecretEnvSourceArgs(
                name=NAME,
            )
        ),
    ]

    kubernetes.batch.v1.CronJob(
        NAME,
        metadata=metadata,
        spec=kubernetes.batch.v1.CronJobSpecArgs(
            schedule=schedule,
            job_template=kubernetes.batch.v1.JobTemplateSpecArgs(
                spec=kubernetes.batch.v1.JobSpecArgs(
                    template=kubernetes.core.v1.PodTemplateSpecArgs(
                        spec=kubernetes.core.v1.PodSpecArgs(
                            restart_policy="Never",
                            containers=[
                                kubernetes.core.v1.ContainerArgs(
                                    name=NAME,
                                    image=image,
                                    env_from=env_from,
                                    volume_mounts=volume_mounts,
                                )
                            ],
                            volumes=volumes,
                        ),
                    ),
                ),
            ),
        ),
    )
