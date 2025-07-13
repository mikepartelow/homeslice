"""Resources for the Unifi auxiliary support."""

import pulumi_kubernetes as kubernetes
import homeslice
import homeslice_config

from homeslice_secrets import (  # pylint: disable=no-name-in-module
    unifi as UNIFI_SECRETS,
    backup_tidal as TIDAL_SECRETS,
)


NAME = "unifi"


def app(config: homeslice_config.UnifiConfig) -> None:
    """define resources for the homeslice/unifi app"""
    image = config.image
    redirect_url = config.redirect_url
    redirect_prefix = config.redirect_prefix
    node_selector = config.node_selector
    schedule = config.schedule

    mount_path = "/mnt/backups"

    homeslice.ingress(
        NAME,
        [redirect_prefix],
        metadata=homeslice.metadata(
            NAME,
            annotations={
                "nginx.ingress.kubernetes.io/permanent-redirect": f"{redirect_url}",
            },
        ),
    )

    config.git_clone_url = UNIFI_SECRETS.GIT_CLONE_URL
    config.ssh_private_key = TIDAL_SECRETS.SSH_PRIVATE_KEY.encode() if TIDAL_SECRETS.SSH_PRIVATE_KEY else None
    btg = homeslice.BackupToGithub(NAME, config)

    homeslice.configmap(NAME, btg.configmap_items)

    _ = btg.ssh_secret  # this line does a lot more than it appears to do!

    kubernetes.core.v1.Secret(  # pylint: disable=duplicate-code
        NAME,
        metadata=homeslice.metadata(NAME),
        type="Opaque",
        string_data=btg.secret_items,
    )

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name=NAME,
            host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                path="/var/lib/unifi/backup/autobackup/",
            ),
        ),
    ]

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=NAME,
            mount_path=mount_path,
            read_only=True,
        ),
    ]

    env_from = [homeslice.env_from_configmap(NAME)]

    homeslice.cronjob(
        f"backup-{NAME}",
        image,
        schedule,
        args=[mount_path],
        node_selector=node_selector,
        env_from=btg.env_from + env_from,
        volumes=btg.volumes + volumes,
        volume_mounts=btg.volume_mounts + volume_mounts,
    )
