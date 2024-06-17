"""Resources for the a Homebridge instance."""

import pulumi
import homeslice
import pulumi_kubernetes as kubernetes

NAME = "homebridge"
PORT = 8581


def app(config: pulumi.Config) -> None:
    image = config["image"]

    ports = [
        kubernetes.core.v1.ContainerPortArgs(
            name="http",
            container_port=PORT,
        )
    ]

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
            mount_path="/homebridge",
        ),
    ]

    homeslice.deployment(
        NAME,
        image,
        host_network=True,
        ports=ports,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )
    homeslice.service(NAME, port=PORT)
