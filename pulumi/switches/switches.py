"""Resources for the homeslice/switches app."""
from pathlib import Path
import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
from homeslice_secrets import switches as SWITCHES_SECRETS

NAME = "switches"


def app(namespace: str, config: pulumi.Config) -> None:
    """define resources for the homeslice/switches app"""

    image = config["image"]
    container_port = int(config["container_port"])
    ingress_enabled = config.get("ingress_enabled", "false") is True
    ingress_prefix = config.get("ingress_prefix")
    switches_json = subst_address(config["switches_json"])
    switches_json_path = config["switches_json_path"]
    switches_json_name = str(Path(switches_json_path).name)
    volume_name = switches_json_name.replace(".", "-")

    metadata = homeslice.metadata(NAME, namespace)

    kubernetes.core.v1.ConfigMap(
        NAME,
        metadata=metadata,
        data={
            switches_json_name: switches_json,
        },
    )

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name=volume_name,
            config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                name=NAME,
            ),
        ),
    ]

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=volume_name,
            mount_path=str(Path(switches_json_path).parent),
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
        NAME,
        image,
        metadata,
        args=[switches_json_path],
        ports=ports,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )

    homeslice.service(NAME, metadata)

    if ingress_enabled:
        homeslice.ingress(NAME, metadata, [ingress_prefix])


# I don't want to publish IP addresses to GitHub
def subst_address(s: str) -> str:
    """Returns the given string with secrets substituted in."""
    for k, v in SWITCHES_SECRETS.IP_ADDRESSES.items():
        s = s.replace(k, v)

    return s
