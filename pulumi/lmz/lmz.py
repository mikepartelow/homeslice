"""Resources for the homeslice/lmz app."""

from pathlib import Path
import pulumi_kubernetes as kubernetes
import pulumi
import homeslice
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    lmz as LMZ_SECRETS,
)

NAME = "lmz"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/lmz app"""

    image = config["image"]
    container_port = int(config["container_port"])
    ingress_prefix = config.get("ingress_prefix")
    lmz_yaml_path = config["lmz_yaml_path"]
    volume_name = NAME

    homeslice.secret(
        NAME,
        string_data={
            Path(lmz_yaml_path).name: LMZ_SECRETS.LMZ_YAML,
        },
    )

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name=volume_name,
            secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                secret_name=NAME,
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

    homeslice.deployment(
        NAME,
        image,
        args=["serve"],
        ports=ports,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )

    homeslice.service(NAME)

    homeslice.ingress(NAME, [ingress_prefix])
