"""Resources for the a Homebridge instance."""

import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
import homeslice_config

PORT = 8581


class Homebridge(pulumi.ComponentResource):
    """Homebridge app resources."""

    def __init__(self, name: str, config: homeslice_config.HomeBridgeConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:homebridge:Homebridge", name, {}, opts)

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
        self.pvc = kubernetes.core.v1.PersistentVolumeClaim(
            name,
            metadata=homeslice.metadata(name),
            spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
                access_modes=["ReadWriteOnce"],
                resources=kubernetes.core.v1.VolumeResourceRequirementsArgs(
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
                name=name,
                persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                    claim_name=name,
                ),
            ),
        ]

        volume_mounts = [
            kubernetes.core.v1.VolumeMountArgs(
                name=name,
                mount_path="/homebridge",
            ),
        ]

        self.deployment = homeslice.deployment(
            name,
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
        self.service = homeslice.service(name, port=PORT, type_="NodePort")

        self.ingress = homeslice.ingress(
            name,
            [redirect_prefix],
            metadata=homeslice.metadata(
                name,
                annotations={
                    "nginx.ingress.kubernetes.io/permanent-redirect": f"http://{redirect_host}:{PORT}",
                },
            ),
        )

        self.register_outputs({})
