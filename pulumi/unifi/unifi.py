"""Resources for the Unifi auxiliary support."""

import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
import homeslice_config
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    unifi as UNIFI_SECRETS,
    backup_tidal as TIDAL_SECRETS,
)


class Unifi(pulumi.ComponentResource):
    """Unifi auxiliary support resources."""

    def __init__(self, name: str, config: homeslice_config.UnifiConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:unifi:Unifi", name, {}, opts)

        image = config.image
        redirect_url = config.redirect_url
        redirect_prefix = config.redirect_prefix
        node_selector = config.node_selector
        schedule = config.schedule

        mount_path = "/mnt/backups"

        self.ingress = homeslice.ingress(
            name,
            [redirect_prefix],
            metadata=homeslice.metadata(
                name,
                annotations={
                    "nginx.ingress.kubernetes.io/permanent-redirect": f"{redirect_url}",
                },
            ),
        )

        config.git_clone_url = UNIFI_SECRETS.GIT_CLONE_URL
        config.ssh_private_key = TIDAL_SECRETS.SSH_PRIVATE_KEY.encode() if TIDAL_SECRETS.SSH_PRIVATE_KEY else None
        btg = homeslice.BackupToGithub(name, config)

        self.configmap = homeslice.configmap(name, btg.configmap_items)

        self.ssh_secret = btg.ssh_secret  # this line does a lot more than it appears to do!

        self.secret = kubernetes.core.v1.Secret(  # pylint: disable=duplicate-code
            name,
            metadata=homeslice.metadata(name),
            type="Opaque",
            string_data=btg.secret_items,
        )

        volumes = [
            kubernetes.core.v1.VolumeArgs(
                name=name,
                host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                    path="/var/lib/unifi/backup/autobackup/",
                ),
            ),
        ]

        volume_mounts = [
            kubernetes.core.v1.VolumeMountArgs(
                name=name,
                mount_path=mount_path,
                read_only=True,
            ),
        ]

        env_from = [homeslice.env_from_configmap(name)]

        self.cronjob = homeslice.cronjob(
            f"backup-{name}",
            image,
            schedule,
            args=[mount_path],
            node_selector=node_selector,
            env_from=btg.env_from + env_from,
            volumes=btg.volumes + volumes,
            volume_mounts=btg.volume_mounts + volume_mounts,
        )

        self.register_outputs({})
