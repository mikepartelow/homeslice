"""Resources for the a Homebridge instance."""

import pulumi_kubernetes as kubernetes
import homeslice
import homeslice_config

NAME = "homebridge"
PORT = 8581


def app(config: homeslice_config.HomeBridgeConfig) -> None:
    """define resources for the homeslice/homebridge app"""
    image = config.image
    redirect_host = config.redirect_host
    redirect_prefix = config.redirect_prefix
    node_selector = config.node_selector

    ports = [
        kubernetes.core.v1.ContainerPortArgs(
            name="http",
            container_port=PORT,
        )
    ]

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
            mount_path="/homebridge",
        ),
    ]

    homeslice.deployment(
        NAME,
        image,
        host_network=True,  # NOTICE THIS
        node_selector=node_selector,
        ports=ports,
        strategy=kubernetes.apps.v1.DeploymentStrategyArgs(
            rolling_update=None,
            type="Recreate",  # because host_network=True, we have to Recreate to release the port
        ),
        volumes=volumes,
        volume_mounts=volume_mounts,
    )
    homeslice.service(NAME, port=PORT)

    homeslice.ingress(
        NAME,
        [redirect_prefix],
        metadata=homeslice.metadata(
            NAME,
            annotations={
                "nginx.ingress.kubernetes.io/permanent-redirect": f"http://{redirect_host}:{PORT}",
            },
        ),
    )
