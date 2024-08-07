"""Resources for the homeslice/lmz app."""

from pathlib import Path
import pulumi_kubernetes as kubernetes
import pulumi
import homeslice
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    switches as SWITCHES_SECRETS,
)

NAME = "lmz"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/lmz app"""

    image = config["image"]
    container_port = int(config["container_port"])
    ingress_prefix = config.get("ingress_prefix")

    # homeslice.secret(
    #     NAME,
    #     {
    #         lmz_yaml_name: lmz_yaml,
    #     },
    # )

    # volumes = [
    #     kubernetes.core.v1.VolumeArgs(
    #         name=volume_name,
    #         config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
    #             name=NAME,
    #         ),
    #     ),
    # ]

    # volume_mounts = [
    #     kubernetes.core.v1.VolumeMountArgs(
    #         name=volume_name,
    #         mount_path=str(Path(switches_json_path).parent),
    #         read_only=True,
    #     ),
    # ]

    ports = [homeslice.port(container_port)]

panic: error during Authorization: Post "https://cms.lamarzocco.io/oauth/v2/token": tls: failed to verify certificate: x509: certificate signed by unknown authority

    homeslice.deployment(
        NAME,
        image,
        args=["serve"],
        ports=ports,
        # volumes=volumes,
        # volume_mounts=volume_mounts,
    )

    homeslice.service(NAME)

    homeslice.ingress(NAME, [ingress_prefix])
