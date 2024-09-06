"""Resources for the Unifi auxiliary support."""

import homeslice_config
import homeslice
import pulumi_kubernetes as kubernetes


NAME = "unifi"


def app(config: homeslice_config.LmzConfig) -> None:
    """define resources for the unifi/unifi app"""
    redirect_url = config.redirect_url
    redirect_prefix = config.redirect_prefix
    node_selector = config.node_selector

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

    homeslice.deployment(
        NAME,
        "busybox",
        command=["sleep", "infinity"],
        node_selector=node_selector,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )


# backup needs host affinity, test that first
