"""Resources for the homeslice/lmz app."""

from pathlib import Path
import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
import homeslice_config
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    lmz as LMZ_SECRETS,
)


class Lmz(pulumi.ComponentResource):
    """Lmz app resources."""

    def __init__(self, name: str, config: homeslice_config.LmzConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:lmz:Lmz", name, {}, opts)

        image = config.image
        container_port = config.container_port
        ingress_prefix = config.ingress_prefix
        lmz_yaml_path = config.lmz_yaml_path
        volume_name = name

        self.secret = homeslice.secret(
            name,
            string_data={
                Path(lmz_yaml_path).name: LMZ_SECRETS.LMZ_YAML,
            },
        )

        volumes = [
            kubernetes.core.v1.VolumeArgs(
                name=volume_name,
                secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                    secret_name=name,
                ),
            ),
        ]

        volume_mounts = [
            kubernetes.core.v1.VolumeMountArgs(
                name=volume_name,
                mount_path=str(Path(lmz_yaml_path).parent),
                read_only=True,
            ),
        ]

        ports = [homeslice.port(container_port)]

        self.deployment = homeslice.deployment(  # pylint: disable=R0801
            name,
            image,
            args=["serve"],
            ports=ports,
            volumes=volumes,
            volume_mounts=volume_mounts,
        )

        self.service = homeslice.service(name)

        if ingress_prefix:
            # pylint: disable=R0801
            self.ingress = homeslice.ingress(
                name,
                [ingress_prefix],
                path_type="ImplementationSpecific",
                metadata=homeslice.metadata(
                    name,
                    annotations={
                        "nginx.ingress.kubernetes.io/use-regex": "true",
                        "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                    },
                ),
            )

        self.register_outputs({})


def app(config: homeslice_config.LmzConfig) -> None:
    """Define resources for the homeslice/lmz app.
    
    Creates an Lmz ComponentResource with deployment, service, optional ingress, and secrets
    for LMZ functionality.
    """
    Lmz("lmz", config)
