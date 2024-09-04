"""Resources for the homeslice/chime app."""

import pulumi_kubernetes as kubernetes
import pulumi
import homeslice
from homeslice_secrets import chime as CHIME_SECRET  # pylint: disable=no-name-in-module

NAME = "chime"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/chime app"""
    image = config["image"]
    chimes = config["chimes"]
    nginx = config["nginx"]
    pvc_mount_path = config["pvc_mount_path"]
    container_port = int(config["container_port"])
    ingress_prefix = config.get("ingress_prefix")

    # an nginx deployment serves up media from a persistent volume
    #
    # pylint: disable=R0801
    kubernetes.core.v1.PersistentVolumeClaim(
        NAME,
        metadata=homeslice.metadata(NAME),
        spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
            access_modes=["ReadWriteOnce"],
            resources=kubernetes.core.v1.ResourceRequirementsArgs(
                requests={
                    "storage": "256Mi",
                },
                limits={
                    "storage": "256Mi",
                },
            ),
        ),
    )

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name=NAME,
            persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                claim_name=NAME,
            ),
        ),
    ]

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=NAME,
            mount_path=pvc_mount_path,
            read_only=True,
        ),
    ]

    ports = [
        kubernetes.core.v1.ContainerPortArgs(
            name="http",
            container_port=container_port,
        )
    ]

    homeslice.deployment(
        NAME, nginx, ports=ports, volumes=volumes, volume_mounts=volume_mounts
    )

    homeslice.service(NAME)

    homeslice.ingress(
        NAME,
        [ingress_prefix],
        path_type="ImplementationSpecific",
        metadata=homeslice.metadata(
            NAME,
            annotations={
                "nginx.ingress.kubernetes.io/use-regex": "true",
                "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
            },
        ),
    )

    # cronjobs schedule the chimes.
    for chime in chimes:
        for zone in CHIME_SECRET.ZONES:
            name = make_name(NAME, chime, zone)
            args = [
                zone["ip_address"],
                chime["media_title"],
                chime["media_uri"].replace("{{ingress}}", CHIME_SECRET.INGRESS),
            ]

            homeslice.cronjob(
                name,
                image,
                chime["schedule"],
                args=args,
                metadata=homeslice.metadata(name),
            )


def make_name(name: str, chime: dict, zone: dict) -> str:
    """Combine the inputs and return a name suitable for a Pulumi URN"""
    boring_title = chime["media_title"].replace(" ", "-")
    boring_zone_name = zone["name"].replace(" ", "-")
    fancy_zone_ip_address = zone["ip_address"].replace(".", "-")
    return (
        name + "-" + boring_title + "-" + fancy_zone_ip_address + "-" + boring_zone_name
    ).lower()
